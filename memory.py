import re
import sys
import win32gui
from ctypes import Structure, c_uint32, c_uint64, c_char, c_ulong, c_ulonglong, sizeof, c_void_p, windll,\
c_size_t, pointer, c_float, cast, c_char_p, byref, create_string_buffer


class PROCESSENTRY32(Structure):
    _fields_ = [
        ("dwSize", c_uint32),
        ("cntUsage", c_uint32),
        ("th32ProcessID", c_uint32),
        ("th32DefaultHeapID", c_uint64),
        ("th32ModuleID", c_uint32),
        ("cntThreads", c_uint32),
        ("th32ParentProcessID", c_uint32),
        ("pcPriClassBase", c_uint32),
        ("dwFlags", c_uint32),
        ("szExeFile", c_char * 260)
    ]

class MEMORY_BASIC_INFORMATION32(Structure):
    _fields_ = [
        ("BaseAddress", c_ulong),
        ("AllocationBase", c_ulong),
        ("AllocationProtect", c_ulong),
        ("RegionSize", c_ulong),
        ("State", c_ulong),
        ("Protect", c_ulong),
        ("Type", c_ulong)
    ]

class MEMORY_BASIC_INFORMATION64(Structure):
    _fields_ = [
        ("BaseAddress", c_ulonglong),
        ("AllocationBase", c_ulonglong),
        ("AllocationProtect", c_ulong),
        ("__alignment1", c_ulong),
        ("RegionSize", c_ulonglong),
        ("State", c_ulong),
        ("Protect", c_ulong),
        ("Type", c_ulong),
        ("__alignment2", c_ulong),
    ]

MEMORY_BASIC_INFORMATION = {8: MEMORY_BASIC_INFORMATION64, 4: MEMORY_BASIC_INFORMATION32}
MEMORY_BASIC_INFORMATION = MEMORY_BASIC_INFORMATION[sizeof(c_void_p)]

class Process:

    @staticmethod
    def get_window_coord(window_name):
        window = win32gui.FindWindow(None, window_name)
        if window != 0:
            rect = win32gui.GetWindowRect(window)
            x = rect[0]
            y = rect[1]
            w = rect[2] - x
            h = rect[3] - y
            return (x, y, w, h)

    @staticmethod
    def get_process_handle(proc_name):
        handle = 0
        entry = PROCESSENTRY32()
        snap = windll.kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
        entry.dwSize = sizeof(PROCESSENTRY32)
        while windll.kernel32.Process32Next(snap, pointer(entry)):
            if entry.szExeFile == proc_name.encode("ascii", "ignore"):
                handle = windll.kernel32.OpenProcess(0x430, 0, entry.th32ProcessID)
                break
        windll.kernel32.CloseHandle(snap)
        return handle

    @staticmethod
    def sleep(ms):
        windll.kernel32.Sleep(ms)

    def __init__(self, proc_name):
        self.process_handle = Process.get_process_handle(proc_name)
        if self.process_handle == 0:
            raise Exception(f"Process {proc_name} not found!")
        else:
            print(f"Process {proc_name} found!")

    def is_running(self):
        exit_code = c_uint32()
        windll.kernel32.GetExitCodeProcess(self.process_handle, pointer(exit_code))
        return exit_code.value == 0x103

    def write_int(self, address, value):
        buffer = c_uint32(value)
        return windll.ntdll.NtWriteVirtualMemory(self.process_handle, address, pointer(buffer), 4, 0) == 0

    def read_int(self, address, length=4):
        buffer = c_uint32()
        windll.ntdll.NtReadVirtualMemory(self.process_handle, address, pointer(buffer), length, 0)
        return buffer.value

    def write_float(self, address, value):
        buffer = c_float(value)
        return windll.ntdll.NtWriteVirtualMemory(self.process_handle, address, pointer(buffer), 4, 0) == 0

    def read_float(self, address, length=4):
        buffer = c_float()
        windll.ntdll.NtReadVirtualMemory(self.process_handle, address, pointer(buffer), length, 0)
        return buffer.value

    def write_bytes(self, address, value, size):
        t_address = cast(address, c_char_p)
        return windll.kernel32.WriteProcessMemory(self.process_handle, t_address, value, size, 0) == 0

    def read_bytes(self, address, size):
        buffer = create_string_buffer(size)
        bytes_read = c_size_t()
        windll.kernel32.ReadProcessMemory(self.process_handle, c_void_p(address), byref(buffer), size, byref(bytes_read))
        return buffer.raw

    def read_string(self, address, size):
        buffer = create_string_buffer(size)
        bytes_read = c_size_t()
        windll.kernel32.ReadProcessMemory(self.process_handle, c_void_p(address), byref(buffer), size, byref(bytes_read))
        return buffer.value.decode('utf-8')

    def get_pointer_address(self, base_address, offsets):
        address = self.read_int(base_address)
        for offset in offsets:
            if offset != offsets[-1]:
                address = self.read_int(address + offset)
        address = address + offsets[-1]
        return address
    
    def find_pattern(self, pattern, *, return_multiple=False):
        next_region, found = 0, []
        user_space_limit = 0x7FFFFFFF0000 if sys.maxsize > 2**32 else 0x7FFF0000
        allowed_protections = [0x10, 0x20, 0x40, 0x04, 0x02]
        virtual_query_ex = windll.kernel32.VirtualQueryEx
        virtual_query_ex.argtypes = [c_void_p, c_void_p, c_void_p, c_size_t]
        virtual_query_ex.restype = c_ulong
        while next_region < user_space_limit:
            mbi = MEMORY_BASIC_INFORMATION()
            virtual_query_ex(self.process_handle, next_region, byref(mbi), sizeof(mbi))
            next_region = mbi.BaseAddress + mbi.RegionSize
            if mbi.State != 0x1000 or mbi.Protect not in allowed_protections:
                continue
            page_bytes = self.read_bytes(mbi.BaseAddress, mbi.RegionSize)
            matches = re.finditer(pattern, page_bytes, re.DOTALL)
            if not return_multiple and (match := next(matches, None)):
                return mbi.BaseAddress + match.span()[0]
            found.extend(mbi.BaseAddress + match.span()[0] for match in matches)
        return found if return_multiple else None