#pragma once

typedef unsigned short spi;

int spi_num_devices();
spi mp_spi_open(int index, int clk_phase, int clk_polarity);
int spi_transfer(spi device, const char* in_data, char* out_data, int length);

