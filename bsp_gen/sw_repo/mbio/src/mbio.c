#include <xparameters.h>
#include <mbio.h>
#include <xil_io.h>

#ifdef XPAR_XGPIO_NUM_INSTANCES

#include <xgpio.h>

// gpio bit format:
// 4:0 low bit
// 9:5 high bit
// 10:10 channel
// 15:11 device

typedef union {
    unsigned short packed;
    struct {
        unsigned short low : 5, high : 5, channel : 1, device : 5;
    } gpio;
} _gpio;

static XGpio _gpio_devices[XPAR_XGPIO_NUM_INSTANCES];

int gpio_num_devices() {
    return XPAR_XGPIO_NUM_INSTANCES;
}

int gpio_channels(int index) {
    XGpio_Config* cfg = XGpio_LookupConfig(index);
    if (cfg->IsDual) return 2;
    else return 1;
}

gpio gpio_open_pin(int index, int channel, int pin) {
    return gpio_open_range(index, channel, pin, pin);
}
gpio gpio_open_range(int index, int channel, int low, int high) {
    if (low >= 32) return -1;
    if (high >= 32) return -1;
    if (low > high) return -1;
    if (index >= XPAR_XGPIO_NUM_INSTANCES) return -1;
    _gpio assignment;
    assignment.gpio.low = low;
    assignment.gpio.high = high;
    assignment.gpio.device = index;
    assignment.gpio.channel = channel;
    return assignment.packed;
}

gpio gpio_open_all(int index, int channel) {
    return gpio_open_range(index, channel, 0, 31);
}

static unsigned int _generate_mask(_gpio assignment) {
    unsigned int high_mask = (1ul << (assignment.gpio.high + 1)) - 1;
    unsigned int low_mask = (1ul << assignment.gpio.low) - 1;
    return high_mask - low_mask;
}

void gpio_set_direction(gpio dev, int direction) {
    _gpio assignment;
    assignment.packed = dev;
    XGpio* device = _gpio_devices + assignment.gpio.device;
    unsigned int mask = _generate_mask(assignment);
    unsigned int directions = XGpio_GetDataDirection(device, assignment.gpio.channel + 1);
    if (direction) {
        directions |= mask;
    } else {
        directions &= ~mask;
    }
    XGpio_SetDataDirection(device, assignment.gpio.channel + 1, directions);
}

void gpio_write(gpio dev, int val) {
    _gpio assignment;
    assignment.packed = dev;
    XGpio* device = _gpio_devices + assignment.gpio.device;

    unsigned int mask = _generate_mask(assignment);
    unsigned int new_val = XGpio_DiscreteRead(device, assignment.gpio.channel + 1);
    new_val &= ~mask;
    new_val |= val << assignment.gpio.low;
    XGpio_DiscreteWrite(device, assignment.gpio.channel + 1, new_val);
}

int gpio_read(gpio dev) {
    _gpio assignment;
    assignment.packed = dev;
    XGpio* device = _gpio_devices + assignment.gpio.device;
    unsigned int mask = _generate_mask(assignment);

    unsigned int values = XGpio_DiscreteRead(device, assignment.gpio.channel + 1);
    return (values & mask) >> assignment.gpio.low;
}

static void gpio_init() {
    for (int i = 0; i < XPAR_XGPIO_NUM_INSTANCES; ++i) {
        XGpio_Initialize(_gpio_devices + i, i);
    }
}

#else // GPIO Definitions

int gpio_num_devices() {
    return 0;
}

gpio gpio_open_pin(int index, int pin, int channel) {
    return -1;
}

gpio gpio_open_range(int index, int low, int high, int channel) {
    return -1;
}

gpio gpio_open_all(int index, int channel) {
    return -1;
}

void gpio_set_direction(gpio dev, int direction) {

}

void gpio_write(gpio dev, int val) {

}

int gpio_read(gpio dev) {
    return -1;
}

static void gpio_init() {

}

#endif // GPIO Definitions


#ifdef  XPAR_XIIC_NUM_INSTANCES

#include <xiic.h>

static unsigned int _i2c_devices[XPAR_XIIC_NUM_INSTANCES];

int i2c_num_devices() {
    return XPAR_XIIC_NUM_INSTANCES;
}

i2c i2c_open(int index) {
    if (index >= XPAR_XIIC_NUM_INSTANCES) return -1;
    return index;
}
int i2c_read(i2c device, unsigned char address, char* data, int length) {
    if (device >= XPAR_XIIC_NUM_INSTANCES) return -1;
    return XIic_Recv(_i2c_devices[device], address, (unsigned char*)data, length, XIIC_STOP);
}
int i2c_write(i2c device, unsigned char address, const char* data, int length) {
    if (device >= XPAR_XIIC_NUM_INSTANCES) return -1;
    return XIic_Send(_i2c_devices[device], address, (unsigned char*)data, length, XIIC_STOP);
}
static void i2c_init() {
    for (int i = 0; i < XPAR_XIIC_NUM_INSTANCES; ++i) {
        XIic_Config* cfg = XIic_LookupConfig(i);
        _i2c_devices[i] = cfg->BaseAddress;
    }
}

#else //I2C Definitions

int i2c_num_devices() {
    return 0;
}
i2c i2c_open(int index) {
    return -1;
}
int i2c_read(i2c device, unsigned char address, char* data, int length) {
    return -1;
}
int i2c_write(i2c device, unsigned char address, const char* data, int length) {
    return -1;
}
static void i2c_init() {

}

#endif //I2C Definitions

#ifdef XPAR_XSPI_NUM_INSTANCES

#include <xspi.h>

static unsigned int _spi_devices[XPAR_XSPI_NUM_INSTANCES];

static void _spi_transfer(u32 BaseAddress, int bytecount,
                  u8* readBuffer, u8* writeBuffer) {
    int i;

    XSpi_WriteReg(BaseAddress,XSP_SSR_OFFSET, 0xfe);
    for (i=0; i<bytecount; i++){
        XSpi_WriteReg(BaseAddress,XSP_DTR_OFFSET, writeBuffer[i]);
    }
    while(((XSpi_ReadReg(BaseAddress,XSP_SR_OFFSET) & 0x04)) != 0x04);
    // Delay loop to remove original code's dependency on a timer
    for (int i = 0; i < 10; ++i) { }

    // Read SPI
    for(i=0;i< bytecount; i++){
       readBuffer[i] = XSpi_ReadReg(BaseAddress,XSP_DRR_OFFSET);
    }
    XSpi_WriteReg(BaseAddress, XSP_SSR_OFFSET, 0xff);
}

static void _spi_init(u32 BaseAddress, u32 clk_phase, u32 clk_polarity){
    u32 Control;

    // Soft reset SPI
    XSpi_WriteReg(BaseAddress, XSP_SRR_OFFSET, 0xa);
    // Master mode
    Control = XSpi_ReadReg(BaseAddress, XSP_CR_OFFSET);
    // Master Mode
    Control |= XSP_CR_MASTER_MODE_MASK;
    // Enable SPI
    Control |= XSP_CR_ENABLE_MASK;
    // Slave select manually
    Control |= XSP_INTR_SLAVE_MODE_MASK;
    // Enable Transmitter
    Control &= ~XSP_CR_TRANS_INHIBIT_MASK;
    // XSP_CR_CLK_PHASE_MASK
    if(clk_phase)
        Control |= XSP_CR_CLK_PHASE_MASK;
    // XSP_CR_CLK_POLARITY_MASK
    if(clk_polarity)
        Control |= XSP_CR_CLK_POLARITY_MASK;
    XSpi_WriteReg(BaseAddress, XSP_CR_OFFSET, Control);
}

int spi_num_devices() {
    return XPAR_XSPI_NUM_INSTANCES;
}

spi mp_spi_open(int index, int clk_phase, int clk_polarity) {
    if (index >= XPAR_XSPI_NUM_INSTANCES) return -1;
    _spi_init(_spi_devices[index], clk_phase, clk_polarity);
    return index;
    
}
int spi_transfer(spi device, const char* in_data, char* out_data, int length) {
    if (device >= XPAR_XSPI_NUM_INSTANCES) return -1;
    _spi_transfer(_spi_devices[device], length, (unsigned char*)in_data, (unsigned char*)out_data);
    return 0;
}

static void spi_device_init() {
    for (int i = 0; i < XPAR_XSPI_NUM_INSTANCES; ++i) {
        XSpi_Config* cfg = XSpi_LookupConfig(i);
        _spi_devices[i] = cfg->BaseAddress;
    }
}
#else // SPI Definitions

int spi_num_devices() {
    return 0;
}
spi mp_spi_open(int index, int clk_phase, int clk_polarity) {
    return -1;
}
int spi_read(spi device, const char* in_data, char* out_data, int length) {
    return -1;
}
static void spi_init() {

}

#endif // SPI Definitions

#ifdef XPAR_XTMRCTR_NUM_INSTANCES

#include <xtmrctr.h>

static XTmrCtr _timer_devices[XPAR_XTMRCTR_NUM_INSTANCES];

int timer_num_devices() {
    return XPAR_XTMRCTR_NUM_INSTANCES;
}

timer timer_open(int index) {
    if (index >= XPAR_XTMRCTR_NUM_INSTANCES) return -1;
    return index;
}

void timer_delay_us(timer timer, int channel, int usdelay) {
    if (timer >= XPAR_XTMRCTR_NUM_INSTANCES) return;

    XTmrCtr* device = _timer_devices + timer;
    XTmrCtr_SetResetValue(device, channel, usdelay*100);
    // Start the timer5 for usdelay us delay
    XTmrCtr_Start(device, channel);
    // Wait for usdelay us to lapse
    while(!XTmrCtr_IsExpired(device, channel));
    // Stop the timer5
    XTmrCtr_Stop(device, channel);
}

void timer_pwm_generate(timer timer, int pulse, int period) {
    unsigned int base_addr = _timer_devices[timer].BaseAddress;
    if (XTmrCtr_ReadReg(base_addr, 0, XTC_TCSR_OFFSET) != 0x296) {
        XTmrCtr_WriteReg(base_addr, 0, XTC_TCSR_OFFSET, 0x296);
        XTmrCtr_WriteReg(base_addr, 1, XTC_TCSR_OFFSET, 0x296);
    }
    XTmrCtr_WriteReg(base_addr, 0, XTC_TLR_OFFSET, period);
    XTmrCtr_WriteReg(base_addr, 1, XTC_TLR_OFFSET, pulse);
}

void timer_pwm_stop(timer timer) {
    unsigned int base_addr = _timer_devices[timer].BaseAddress;
    XTmrCtr_WriteReg(base_addr, 0, XTC_TCSR_OFFSET, 0);
    XTmrCtr_WriteReg(base_addr, 1, XTC_TCSR_OFFSET, 0);
}

static void timer_init() {
    for (int i = 0; i < XPAR_XTMRCTR_NUM_INSTANCES; ++i) {
        XTmrCtr_Initialize(_timer_devices + i, i);
        XTmrCtr_SetOptions(_timer_devices + i, 0, 
            XTC_AUTO_RELOAD_OPTION | XTC_CSR_LOAD_MASK | XTC_CSR_DOWN_COUNT_MASK);
        XTmrCtr_SetOptions(_timer_devices + i, 1, 
            XTC_AUTO_RELOAD_OPTION | XTC_CSR_LOAD_MASK | XTC_CSR_DOWN_COUNT_MASK);
    }
}

#else // Timer Definitions

int timer_num_devices() {
    return 0;
}

timer timer_open(int index) {
    return -1;
}

void timer_delay_us(timer timer, int channel, int usdelay) {
}

void timer_pwm_generate(timer timer, int pulse, int period) {

}

void timer_pwm_stop(timer timer) {

}

static void timer_init() {

}

#endif // Timer Definitions

#ifdef XPAR_XSYSMON_NUM_INSTANCES

#include <xsysmon.h>

static XSysMon sysmon;

int analog_num_devices() { return 16; }
analog analog_open(int index) {
    if (index >= 16) return -1;
    return index;
}

int analog_read_raw(analog adc) {
    if (adc >= 16) return 0;
    return XSysMon_GetAdcData(&sysmon, XSM_CH_AUX_MIN + adc);
}

static void adc_init() {
    XSysMon_Config* cfg = XSysMon_LookupConfig(0);
    XSysMon_CfgInitialize(&sysmon, cfg, cfg->BaseAddress);
    // Clear the old status
    XSysMon_GetStatus(&sysmon);
}

int analog_range(analog adc) {
    return 65536;
}
float analog_vref(analog adc) {
    return 3.3f;
}

#else // Analog definitions

int analog_num_devices() { return 0; }
analog analog_open(int index) { return -1; }
int analog_read_raw(analog adc) { return 0; }
int analog_range(analog adc) { return 0; }
float analog_vref(analog adc) { return 0.0f; }
static void adc_init() {}

#endif // Analog definitions

float analog_read(analog adc) {
    return (analog_read_raw(adc) * analog_vref(adc)) / (analog_range(adc));
}

static timer _delay_timer = -1;
static int _delay_channel;

int delay(int ms) {
    return delayMicroseconds(ms * 1000);
}

int delayMicroseconds(int us) {
    if (_delay_timer == -1) return -1;
    timer_delay_us(_delay_timer, _delay_channel, us);
    return 0;
}

void timer_set_as_default(timer timer, int channel) {
    _delay_timer = timer;
    _delay_channel = channel;
}

__attribute__((constructor(900)))
static void mb_io_init() {
     gpio_init();
     i2c_init();
     spi_device_init();
     timer_init();
     adc_init();
}
