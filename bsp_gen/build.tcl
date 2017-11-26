if {$argc != 2} {
    puts "Usage build.tcl workspace hdf"
    exit 1
}

setws [lindex $argv 0]
repo -set [pwd]/sw_repo

createhw -name hw_proj -hwspec [lindex $argv 1]
# open_hw_design /home/xilinxfae/top.hdf

proc connected_to {net ip} {
    set pins [hsi::get_pins -of $net]
    set candidates {}
    foreach pin $pins {
        if {[string equal $pin en]} {
            lappend candidates [hsi::get_cells -of $pin]
        }
    }
    return $candidates
}

proc find_interrupt_gpio {ips} {
    set interrupts {}
    foreach ip $ips {
        set pins [hsi::get_pins -of $ip]
        set pin_index [lsearch $pins gpio_io_o]
        if {$pin_index >= 0} {
            set pin [lindex $pins $pin_index]
            set nets [hsi::get_nets -of $pin]
            if {[llength $nets] > 0} {
                set connected [connected_to [hsi::get_nets -of $pin] $ip]
                foreach candidate $connected {
                    if {[hsi::get_property VLNV $candidate] == "xilinx.com:XUP:dff_en_reset:1.0"} {
                        lappend interrupts $ip
                    }
                }
            }
        }
    }
    return $interrupts
}

proc find_ip {ips name} {
    return [hsi::get_cells -filter "IP_NAME == $name" $ips]
}



set processors [hsi::get_cells -filter {IP_TYPE == PROCESSOR && IP_NAME == microblaze}]

foreach mb $processors {
    set ips [hsi::get_cells [hsi::get_property SLAVES $mb]]
    set interrupt [find_interrupt_gpio $ips]
    set bram [find_ip $ips lmb_bram_if_cntlr]
    set pmod_switch [find_ip $ips pmod_io_switch]
    set arduino_switch [find_ip $ips arduino_io_switch]

    puts "Creating BSP for $mb"
    set bsp "${mb}_bsp"
    createbsp -name $bsp -proc $mb -hwproject hw_proj -os standalone
    set gpios [find_ip $ips axi_gpio]
    foreach gpio $gpios {
        if {[string equal $gpio $interrupt]} {
            setdriver -bsp $bsp -ip $gpio -driver "intrgpio" -hw hw_proj
        } else {
            setdriver -bsp $bsp -ip $gpio -driver "gpio" -hw hw_proj
        }
    }
    setdriver -bsp $bsp -ip $bram -driver "mailbox_bram" -hw hw_proj
    configbsp -bsp $bsp -hw hw_proj stdin $bram
    configbsp -bsp $bsp -hw hw_proj stdout $bram
    foreach ip $pmod_switch {
        setdriver -bsp $bsp -ip $ip -driver "mb_pmod" -hw hw_proj
    }
    foreach ip $arduino_switch {
        setdriver -bsp $bsp -ip $ip -driver "mb_arduino" -hw hw_proj
    }
    setlib -bsp $bsp -hw hw_proj -lib mbio
    regenbsp -bsp $bsp -hw hw_proj
    # createapp -app "Empty Application" -proc $mb -hwproject hw_proj -bsp $bsp -os standalone -lang c -name "${mb}_app"
}

puts "Building BSPs"
projects -build
