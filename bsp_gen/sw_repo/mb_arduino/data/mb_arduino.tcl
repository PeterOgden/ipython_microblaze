

proc generate {drv_handle} {
	xdefine_include_file $drv_handle "xparameters.h" "arduino_io_switch" "NUM_INSTANCES" "DEVICE_ID"  "C_S_AXI_BASEADDR" "C_S_AXI_HIGHADDR"
	::hsi::utils::define_canonical_xpars $drv_handle "xparameters.h" "c_arduino_io_switch" "C_S_AXI_BASEADDR" "C_S_AXI_HIGHADDR" "DEVICE_ID"
}
