#include <ledbar.h>

typedef unsigned char u8;

void send_data(ledbar info, u8 data){
    int i;
    u8 data_state, clk_state, detect, data_internal;

    data_internal = data;

    int clkval = 0;
    // Pad the upper 8 bits
    for (i = 0; i < 8; ++i) {
        clkval ^= 1;
        gpio_write(info.data, 0);
        gpio_write(info.clk, clkval);
    }

    // Working in 8-bit mode
    for (i = 0; i < 8; i++){
        /*
         * Read each bit of the data to be sent LSB first
         * Write it to the data_pin
         */
        data_state = (data_internal & 0x80) ? 0x00000001 : 0x00000000;
        gpio_write(info.data, data_state);
        clkval ^= 1;
        gpio_write(info.clk, clkval);

        // Shift Incoming data to fetch next bit
        data_internal = data_internal << 1;
    }
}

void latch_data(ledbar info){
    int i;
    gpio_write(info.data, 0);
    delay(10);
    // Generate four pulses on the data pin as per data sheet
    for (i = 0; i < 4; i++){
        gpio_write(info.data, 1);
        gpio_write(info.data, 0);
    }
}

void ledbar_set_level(ledbar info, u8 val) {
    val = 10 - val;
    send_data(info, 0x00);
    for (int i = 0; i < 10; ++i) {
        send_data(info, i >= val? 0xFF: 0x00);
    }
    send_data(info, 0x00);
    send_data(info, 0x00);
    latch_data(info);
}

void ledbar_set_data(ledbar info, u8 val[10]) {
    send_data(info, 0x00);
    for (int i = 0; i < 10; ++i) {
        send_data(info, val[i]);
    }
    send_data(info, 0x00);
    send_data(info, 0x00);
    latch_data(info);
}

ledbar ledbar_init(unsigned char port) {
    ledbar info;
    info.data = gpio_connect_grove(port, 0);
    info.clk = gpio_connect_grove(port, 1);
    gpio_set_direction(info.data, GPIO_OUT);
    gpio_set_direction(info.clk, GPIO_OUT);
    return info;
}
