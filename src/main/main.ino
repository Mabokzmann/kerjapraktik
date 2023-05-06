#define pinVoltPV    A1 // Tegangan PV
#define pinCurPV     A2 // Arus PV
#define pinVoltVAWT  A3 // Tegangan VAWT
#define pinCurVAWT   A4 // Arus VAWT
#define pinVoltBat   A5 // Tegangan Baterai

#define pinR1   3
#define pinR2   4
#define pinR3   5
#define pinR4   6

#define read_time       500     // Dalam ms
#define one_rotation    36      // Pergantian hitam ke putih
#define circumference   0.5654  // Dalam satuan meter
#define pinWind         2       // Anemometer

float R1 = 30000, R2 = 7500;
float R3 = 29800, R4 = 6500;
float VRef = 5;

volatile unsigned long rotation = 0;
unsigned long start_time = 0;
unsigned long sampling = 0;
unsigned long send_data = 0;

float iter_wind = 0;
float iter_sampling = 0;

typedef struct {
  float v_pv = 0;
  float i_pv = 0;
  float p_pv = 0;
  float v_vawt = 0;
  float i_vawt = 0;
  float p_vawt = 0;
  float anemo = 0;
  float v_bat = 0;
  } data;
data Sensor;

void addRotation() {
  rotation++;
}

float conv(float num){
  if (num < 0){
    return 0;
  } else {
    return num;
  }
}

float ReadVoltPV() {
  unsigned long samples = 0;
  float avr = 0, value_v = 0;
  for (int x = 0; x < 200; x++){
    samples += analogRead(pinVoltPV);
    delay(2);
  }
  avr = samples/200.00;
  value_v = ( avr * VRef ) / 1024;
  value_v = value_v / (R2 / (R1 + R2));
  return conv(0.9781*value_v + 0.0188);
}

float ReadVoltVAWT() {
  unsigned long samples = 0;
  float avr = 0, value_v = 0;
  for (int x = 0; x < 200; x++){
    samples += analogRead(pinVoltVAWT);
    delay(2);
  }
  avr = samples/200.00;
  value_v = ( avr * VRef ) / 1024;
  value_v = value_v / (R2 / (R1 + R2));
  return conv(0.9697*value_v - 0.0093);
}

float ReadCurPV() {
  unsigned long samples = 0;
  float avr = 0, value_i = 0;
  for (int x = 0; x < 200; x++){
    samples += analogRead(pinCurPV);
    delay(2);
  }
  avr = samples/200.00;
  value_i = (((2.5 - (avr * ((5.0) / 1024.0)) )/0.066)*6.25)/6.27;
  return conv(0.9885*abs(value_i) - 0.1779);
}

float ReadCurVAWT() {
  unsigned long samples = 0;
  float avr = 0, value_i = 0;
  for (int x = 0; x < 200; x++){
    samples += analogRead(pinCurVAWT);
    delay(2);
  }
  avr = samples/200.00;
  value_i = (((2.5 - (avr * ((5.0) / 1024.0)) )/0.066)*6.25)/18.30;
  return conv(4.8333*abs(value_i) - 2.4167);
}

float ReadVoltBat() {
  unsigned long samples = 0;
  float avr = 0, value_v = 0;
  for (int x = 0; x < 200; x++){
    samples += analogRead(pinVoltBat);
    delay(2);
  }
  avr = samples/200.00;
  value_v = ( avr * VRef ) / 1024;
  value_v = value_v / (R4 / (R3 + R4));
  return conv(0.9334*value_v - 0.4085);
}

void setup() {
  Serial.begin (9600);
  
  pinMode(pinWind, INPUT_PULLUP);
  pinMode(pinR1, OUTPUT);
  pinMode(pinR2, OUTPUT);
  pinMode(pinR3, OUTPUT);
  pinMode(pinR4, OUTPUT);
  
  digitalWrite(pinR1, HIGH);
  digitalWrite(pinR2, HIGH);
  digitalWrite(pinR3, HIGH);
  digitalWrite(pinR4, HIGH);
  
  digitalWrite(pinR1, LOW);
  delay(500);
  digitalWrite(pinR1, HIGH);
  delay(500);
  digitalWrite(pinR2, LOW);
  delay(500);
  digitalWrite(pinR2, HIGH);
  delay(500);
  digitalWrite(pinR3, LOW);
  delay(500);
  digitalWrite(pinR3, HIGH);
  delay(500);
  digitalWrite(pinR4, LOW);
  delay(500);
  digitalWrite(pinR4, HIGH);
  
  attachInterrupt(digitalPinToInterrupt(pinWind), addRotation, CHANGE);
  sei();  //Enables Interrupts
  start_time = millis();
  send_data = millis();
  sampling = millis();
  }

void loop() {
    
  if ((unsigned long)(millis() - sampling) >= 10000) {
    sampling = millis();
    Sensor.v_pv += ReadVoltPV();
    Sensor.v_vawt += ReadVoltVAWT();
    Sensor.i_vawt += ReadCurVAWT();
    Sensor.p_vawt += Sensor.v_vawt*Sensor.i_vawt;
    Sensor.v_bat += ReadVoltBat();
    iter_sampling += 1;  
  }
      
  if ((unsigned long)(millis() - start_time) >= read_time) {
    cli();  //Disable Interrupts
    iter_wind += 1;
    Sensor.anemo += ((circumference * rotation * 4 / one_rotation)/4.1);
    rotation = 0;
    start_time = millis();
    sei();  //Enables Interrupts
  }

  if ((unsigned long)(millis() - send_data) >= 120000) {
    send_data = millis();
    digitalWrite(pinR1, LOW);
    delay(500);
    digitalWrite(pinR2, LOW);
    delay(500);
    digitalWrite(pinR3, LOW);
    delay(500);
    digitalWrite(pinR4, LOW);
    delay(2500);
    Sensor.v_pv = Sensor.v_pv/iter_sampling;
    Sensor.i_pv = ReadCurPV();
    Sensor.v_vawt = Sensor.v_vawt/iter_sampling;
    Sensor.i_vawt = Sensor.i_vawt/iter_sampling;
    Sensor.p_pv = Sensor.v_pv*Sensor.i_pv;
    Sensor.p_vawt = Sensor.p_vawt/iter_sampling;
    Sensor.anemo = Sensor.anemo/iter_wind;
    Sensor.v_bat = Sensor.v_bat/iter_sampling;
    Serial.write("&");
    Serial.write("*");
    Serial.write("%");
    Serial.write((const byte*)&Sensor, sizeof(Sensor));
    Sensor.v_pv = 0;
    Sensor.i_pv = 0;
    Sensor.v_vawt = 0;
    Sensor.i_vawt = 0;
    Sensor.p_pv = 0;
    Sensor.p_vawt = 0;
    Sensor.anemo = 0;
    Sensor.v_bat = 0;
    iter_sampling = 0;
    iter_wind = 0;
    delay(2500);
    digitalWrite(pinR1, HIGH);
    delay(500);
    digitalWrite(pinR2, HIGH);
    delay(500);
    digitalWrite(pinR3, HIGH);
    delay(500);
    digitalWrite(pinR4, HIGH);
  }
}
