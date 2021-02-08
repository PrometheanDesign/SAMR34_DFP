# This file is autogenerated
comm_speed=4000000
printDebug = False
logLevel = 0

def begin_communication_session():
    global comm_iface, comm_speed
    comm_iface = settings.getString("communication.interface", "swd") == "swd"
    comm_speed = settings.getNumeric("communication.frequency", comm_speed)
    dev.Connect(comm_iface, comm_speed)
    dev.SetApiLogging(logLevel)
    log.setShowOutput(printDebug)
    if "RH71" in device:
        initialize_HEFC()

def begin_debug_session():#mplab
    log.info("Debug: Init debug session")
    reset_target()
    
def debug_read(mem_type, start, length, data):#mplab
    log.info("Debug: Reading %d bytes at start address 0x%08x (%s)" % (length, start, mem_type))
    dev.Read(start, data, 0, length)

def debug_write(mem_type, start, length, data):#mplab
    log.info("Debug: Writing %d bytes at start address 0x%08x (%s)" % (length, start, mem_type))
    dev.Write(start, data, 0, length)

def get_pc():#mplab
    return dev.ReadReg64(arm.PC)

def run_target():#mplab
    log.info("Debug: run target")
    dev.GoEx(1, 1)

def halt_target():#mplab
    log.info("Debug: halt target")
    dev.Halt()

def step_target():#mplab
    log.info("Debug: stepping at pc 0x%08x" % get_pc())
    dev.Step()

def set_pc(pc):#mplab
    log.info("Debug: set pc to 0x%08x" % pc)
    dev.WriteReg64(arm.PC, pc)

def reset_target(): # mplab
    log.info("Debug: reset")
    dev.Reset()
    on_after_reset() # call autoload hook

g_stopped = False

def is_target_running(): # mplab
    global g_stopped

    stopped = dev.IsHalted()
    if stopped != g_stopped:
        log.info("Debug: target has halted" if stopped else "Debug: target is now running")
        g_stopped = stopped
    return 0  == g_stopped

def end_debug_session():  # mplab
    log.info("Debug: End debug session")

def on_after_reset():  # hook to be overwritten in autoload.py
    try:
        vtor=deb.GetSymbolAddress("exception_table")
        load_vtor(vtor) 
    except:
        pass        
    pass

def load_vtor(adr):
    try:
        dev.WriteReg64(arm.PC,dev.Read32(adr + 4))
        dev.WriteReg64(arm.SP,dev.Read32(adr))
    except:
        log.error("Debug: failed to set PC and SP to contents of exception_table")

def on_program_done():
    on_after_reset()
def write_config(address, len, data):
    dev.Write(address,data,0,len)

def read_config(address, length, data):
    dev.Read(address, data, 0, length)
def erase(): # mplab
    # looks like dev erases as it goes. No need for a whole chip erase
    log.info("Prog: Erase")
    dev.Halt()
    dev.api.JLINK_EraseChip()
    dev.Delay(100000)


def prog_write(type_of_mem, address, length, data): # mplab
    log.info("Writing %d bytes to address 0x%0x of %s memory" % (length, address, type_of_mem))
    if str(type_of_mem) == "Cfg":
        write_config(address, length, data)
        return  # This should never be reached...
    elif str(type_of_mem) != "Pgm":
        dev.Write(address, data, 0, length)
        return

    dev.Write(address, data, 0, length)

def prog_read(type_of_mem, address, length, data): # mplab
    log.info("Reading %d bytes from address 0x%0x of %s memory" % (length, address, type_of_mem))
    if str(type_of_mem) == "Cfg":
        read_config(address, length, data)
        return
    dev.Read(address, data, 0, length)


def end_of_operations(): # mplab
    log.info("Prog: End of operations")
    dev.Reset()

def get_sp():
    return dev.ReadReg64(arm.SP)

def set_sp(sp):
    log.info("Debug: Set sp to 0x%0x" % sp)
    dev.WriteReg64(arm.SP, sp)

