#include <ledbar.h>
#include <iop_switch.h>

typedef unsigned char u8;

typedef struct {
     mb_gpio data;
     mb_gpio clk;
} ledbar_info;

void send_data(ledbar_info info, u8 data){
    int i;
    u8 data_state, clk_state, detect, data_internal;

    data_internal = data;

    int clkval = 0;
    // Pad the upper 8 bits
    for (i = 0; i < 8; ++i) {
        clkval ^= 1;
        mb_gpio_write(info.data, 0);
        mb_gpio_write(info.clk, clkval);
    }

    // Working in 8-bit mode
    for (i = 0; i < 8; i++){
        /*
         * Read each bit of the data to be sent LSB first
         * Write it to the data_pin
         */
        data_state = (data_internal & 0x80) ? 0x00000001 : 0x00000000;
        mb_gpio_write(info.data, data_state);
        clkval ^= 1;
        mb_gpio_write(info.clk, clkval);

        // Shift Incoming data to fetch next bit
        data_internal = data_internal << 1;
    }
}

void latch_data(ledbar_info info){
    int i;
    mb_gpio_write(info.data, 0);
    delay(10);
    // Generate four pulses on the data pin as per data sheet
    for (i = 0; i < 4; i++){
        mb_gpio_write(info.data, 1);
        mb_gpio_write(info.data, 0);
    }
}

void ledbar_set_level(ledbar lb, u8 val) {
    ledbar_info info = {lb >> 16, lb & 0xFFFF};
    val = 10 - val;
    send_data(info, 0x00);
    for (int i = 0; i < 10; ++i) {
        send_data(info, i >= val? 0xFF: 0x00);
    }
    send_data(info, 0x00);
    send_data(info, 0x00);
    latch_data(info);
}

void ledbar_set_data(ledbar lb, const u8* val) {
    ledbar_info info = {lb >> 16, lb & 0xFFFF};
    send_data(info, 0x00);
    for (int i = 0; i < 10; ++i) {
        send_data(info, val[i]);
    }
    send_data(info, 0x00);
    send_data(info, 0x00);
    latch_data(info);
}

ledbar ledbar_open(mb_gpio data, mb_gpio clk) {
    mb_gpio_set_direction(data, GPIO_OUT);
    mb_gpio_set_direction(clk, GPIO_OUT);
    return ((unsigned int)data << 16) | clk;

}

ledbar ledbar_open_grove(unsigned char port) {
    return ledbar_open(
        iop_switch_gpio_grove(port, 0),
        iop_switch_gpio_grove(port, 1));
}
