# Ensure correct number of arguments are provided
if {[llength $argv] < 1 || [llength $argv] > 2} {
    puts "Usage: xsct flash_board.tcl <boot_root_path> [bitstream_path]"
    exit 1
}

# Assign command-line arguments to variables
set boot_root_path [lindex $argv 0]
set bitstream_path ""

# Check if a second argument (bitstream path) is provided
if {[llength $argv] == 2} {
    set bitstream_path [lindex $argv 1]
}

# Connect to target
connect

# Disable Security gates to view PMU MB target
targets -set -nocase -filter {name =~ "*PSU*"}
rst
mask_write 0xFFCA0038 0x1C0 0x1C0

# Load FPGA bitstream if provided
if {$bitstream_path ne ""} {
    fpga $bitstream_path
}

#Load and run PMU FW
targets -set -nocase -filter {name =~ "*MicroBlaze PMU*"}
dow $boot_root_path/pmufw.elf
con
after 500

# Load and run FSBL
targets -set -nocase -filter {name =~ "*A53*#0"}
rst -proc
dow $boot_root_path/zynqmp_fsbl.elf
con
after 5000
stop

# Load DTB at 0x100000
dow -data $boot_root_path/system.dtb 0x100000
after 5000

# Load and run u-boot
dow $boot_root_path/u-boot.elf
dow $boot_root_path/bl31.elf
con

# Disconnect from the target
disconnect

puts "Programming completed."
