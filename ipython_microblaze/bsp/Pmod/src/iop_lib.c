#include <iop_switch.h>
#include <iop.h>
#include <iop_l.h>

#define MAX_I2C 2

static unsigned short i2c_config[MAX_I2C];

void i2c_set_config(i2c config, switch_handle h) {
    if (config != i2c_config[h]) {
        if (config >= 0x8000) {
           i2c_connect_grove(config & 0xFF);
        } else {
           i2c_connect(config & 0xFF, config >> 8);
        }
        i2c_config[h] = config;
    }
}

i2c i2c_connect_grove(unsigned char port) {
    switch_handle h = iop_switch_i2c_grove(port);
    i2c config = 0x8000 | port;
    i2c_config[h] = config;
    return config | (h << 16);
}

i2c i2c_connect(unsigned char scl, unsigned char sda) {
    switch_handle h = iop_switch_i2c_raw(scl, sda);
    i2c config = ((int)sda << 8) | scl;
    i2c_config[h] = config;
    return config | (h << 16);
}

void i2c_write(i2c instance, unsigned char address, unsigned char* data, int length) {
    switch_handle h = instance  >> 16;
    unsigned short config = instance & 0xFFFF;
    i2c_set_config(config, h);
    iop_i2c_write(h, address, data, length);
}

void i2c_read(i2c instance, unsigned char address, unsigned char* data, int length) {
    switch_handle h = instance  >> 16;
    unsigned short config = instance & 0xFFFF;
    i2c_set_config(config, h);
    iop_i2c_read(h, address, data, length);
}

gpio gpio_connect(unsigned char pin) {
    return iop_switch_gpio_raw(pin);
}

gpio gpio_connect_grove(unsigned char port, unsigned char wire) {
    return iop_switch_gpio_grove(port, wire);
}

void gpio_write(gpio channel, unsigned char value) {
    iop_gpio_write((switch_handle)channel, value);
}

unsigned char gpio_read(gpio channel) {
    return iop_gpio_read((switch_handle)channel);
}

void gpio_set_direction(gpio channel, unsigned char direction) {
    iop_gpio_set_direction((switch_handle)channel, direction);
}

void delayMicroseconds(int us) {
    iop_delay(us);
}

void delay(int ms) {
    delayMicroseconds(ms * 1000);
}

pwm pwm_connect(unsigned char pin) {
    return iop_switch_pwm_raw(pin);
}

pwm pwm_connect_grove(unsigned char port, unsigned char wire) {
    return iop_switch_pwm_grove(port, wire);
}

void pwm_generate_cycles(pwm timer, int period, int pulse) {
    iop_pwm_generate_cycles((switch_handle)timer, period, pulse);
}

void pwm_generate_us(pwm timer, int period, int pulse) {
    pwm_generate_cycles(timer, period * 100, pulse * 100);
}

void pwm_stop(pwm timer) {
    iop_pwm_stop((switch_handle)timer);
}

/* The ADC int is packed in a pretty dense way to fit everythin into 32 bits

  31:24 : adc I2C address
     23 : 1 -> I2C, 0 -> Analog
  22: 0 : i2c data or analog handle

*/

#define ADC_I2C_FLAG (1u << 23)
typedef unsigned int u32;
typedef unsigned char u8;

u32 _read_adc(i2c device, unsigned int address, u8 reg){
   u8 data_buffer[2];
   u32 sample;

   data_buffer[0] = reg; // Set the address pointer register
   i2c_write(device, address, data_buffer, 1);

   i2c_read(device, address, data_buffer, 2);
   sample = ((data_buffer[0]&0x0f) << 8) | data_buffer[1];
   return sample;
}


// Write a number of bytes to a Register
// Maximum of 2 data bytes can be written in one transaction
void _write_adc(i2c device, unsigned int address, u8 reg, u32 data, u8 bytes){
   u8 data_buffer[3];
   data_buffer[0] = reg;
   if(bytes ==2){
      data_buffer[1] = (data >> 8) & 0x0f; // Bits 11:8
      data_buffer[2] = data & 0xff; // Bits 7:0
   }else{
      data_buffer[1] = data & 0xff; // Bits 7:0
   }

   i2c_write(device, address, data_buffer, bytes+1);
}
adc adc_connect(unsigned char pin) {
    return iop_switch_analog_raw(pin);
}

adc adc_connect_grove(unsigned char port, unsigned char wire) {
    return iop_switch_analog_grove(port, wire);
}

adc adc_connect_i2c(i2c bus, unsigned int address) {
    // Write the config register
    _write_adc(bus, address, 2, 0x20, 1);
    return bus | ADC_I2C_FLAG | (address << 24);
}

int adc_read_raw(adc device) {
     if (device & ADC_I2C_FLAG) {
         i2c bus = device & 0x7FFFF;
         unsigned int address = device >> 24;
         return _read_adc(bus, address, 0);
     } else {
         return iop_analog_read(device);
     }
}

float adc_read(adc device) {
     int raw = adc_read_raw(device);
     if (device & ADC_I2C_FLAG) {
         return raw * (3.1f / 2048);
     } else {
         return raw * (iop_analog_vref(device) / iop_analog_range(device));
     }
}

