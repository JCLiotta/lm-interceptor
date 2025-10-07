/*************************************************************
Motor Shield 2-Channel DC Motor

*************************************************************/

#include <Wire.h>

#define SLAVE_ADDRESS 0x04
int number = 0;

const int ChAMotorPin = 12;
const int ChABrakePin = 9;

const int ChBMotorPin = 13;
const int ChBBrakePin = 8;

const int LeftMotorPin = 11;
const int RightMotorPin = 3;

const int LEFT_WHEEL = 1;
const int RIGHT_WHEEL = 2;
const int BOTH_WHEELS = 3;
const int STOP_WHEELS = 4;
int state = 0;
void setup() 
{

  //Setup I2C
  Serial.begin(9600); // start serial for output
  // initialize i2c as slave
  Wire.begin(SLAVE_ADDRESS);

  // define callbacks for i2c communication
  Wire.onReceive(receiveData);
  //Wire.onRequest(sendData);

  Serial.println("Ready!");
  
  //Setup Channel A
  pinMode(ChAMotorPin, OUTPUT); //Initiates Motor Channel A pin
  pinMode(ChABrakePin, OUTPUT); //Initiates Brake Channel A pin

  //Setup Channel B
  pinMode(ChBMotorPin, OUTPUT); //Initiates Motor Channel B pin
  pinMode(ChBBrakePin, OUTPUT);  //Initiates Brake Channel B pin

  digitalWrite(ChABrakePin, LOW);
  digitalWrite(ChBBrakePin, LOW);

  //Establish forward direction on channels
  digitalWrite(ChAMotorPin, LOW); //Establishes forward direction of Channel A
  digitalWrite(ChBMotorPin, HIGH); //Establishes forward direction of Channel B
   
}

void loop()
{
  
  switch(state)
  {
    case LEFT_WHEEL:
    //Motor B forward @ full speed
    //digitalWrite(ChBMotorPin, HIGH); //Establishes forward direction of Channel B
    //analogWrite(RightMotorPin, 192);   //Spins the motor on Channel B at 1/2 full speed  
    analogWrite(RightMotorPin, 100);   //Spins the motor on Channel B at 1/2 full speed  
            
    //Break Motor A
    analogWrite(LeftMotorPin, 0);
    Serial.println("Spin Right Wheel!");
    break;
    
    case RIGHT_WHEEL:
    //Motor A forward @ full speed
    //digitalWrite(ChAMotorPin, LOW); //Establishes forward direction of Channel A
    //analogWrite(LeftMotorPin, 192);   //Spins the motor on Channel A at 1/2 full speed
    analogWrite(LeftMotorPin, 100);   //Spins the motor on Channel A at 1/2 full speed


    //Break Motor B
    analogWrite(RightMotorPin, 0);
    Serial.println("Spin Left Wheel!");
    break;

    case BOTH_WHEELS:
    //Motor A forward @ full speed
    //digitalWrite(ChAMotorPin, LOW); //Establishes forward direction of Channel A
    analogWrite(LeftMotorPin, 192);   //Spins the motor on Channel A at 1/2 speed
    //Motor B forward @ full speed
    //digitalWrite(ChBMotorPin, HIGH); //Establishes forward direction of Channel B
    analogWrite(RightMotorPin, 192);   //Spins the motor on Channel B at 1/2 speed  
    Serial.println("Spin Both Wheel!");
    break;

    case STOP_WHEELS:
    //Break Motor A
    analogWrite(LeftMotorPin, 0);
    //Break Motor B
    analogWrite(RightMotorPin, 0);
    Serial.println("Stop Both Wheels!");
    break;
    default:
    analogWrite(LeftMotorPin, 0);
    analogWrite(RightMotorPin, 0);
  }
  
  //delay(125);
  
}

void receiveData(int byteCount)
{

  while(Wire.available()) 
  {
    state = Wire.read();
    Serial.print("data received: ");
    Serial.println(state);

  }
}

