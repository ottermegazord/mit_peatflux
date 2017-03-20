#include <TimerOne.h>
#include <LiquidCrystal.h>
// This example creates a PWM signal with 25 kHz carrier.
//
// Arduino's analogWrite() gives you PWM output, but no control over the
// carrier frequency.  The default frequency is low, typically 490 or
// 3920 Hz.  Sometimes you may need a faster carrier frequency.
//
// The specification for 4-wire PWM fans recommends a 25 kHz frequency
// and allows 21 to 28 kHz.  The default from analogWrite() might work
// with some fans, but to follow the specification we need 25 kHz.
//
// http://www.formfactors.org/developer/specs/REV1_2_Public.pdf
//
// Connect the PWM pin to the fan's control wire (usually blue).  The
// board's ground must be connected to the fan's ground, and the fan
// needs +12 volt power from the computer or a separate power supply.

const int fanPin = 10; // PWM pin 10
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);


void setup(void)
{
  
  pinMode(2, OUTPUT);
  Timer1.initialize(40);  // 40 us = 25 kHz
  Serial.begin(9600);
  lcd.begin(16, 2);
  
}

void loop(void)
{
    int sensorValue = analogRead(A0); // stores voltage in bits
    int pwmspeed; // rounds off bits to int

    float voltage = sensorValue * (5.0 / 1023.0); //converts to voltage
    pwmspeed = voltage / 5.0 * 1023; //redefines pwm speed
    float cycle; 
    cycle = pwmspeed/1023.0 * 100;  
    
    lcd.setCursor(0, 0);
    lcd.print("Pot V: ");
    lcd.setCursor(7, 0);
    

    //"if" statements to reset lcd whenever the bit speeds hit that value
    //this is to resolve the printing issue with the lcd
    //the bit speed must hit the value in the if statement for the lcd to reset
    
//    if ( pwmspeed == 999 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 905 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 951 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 888 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 844 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 777 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 666 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 555 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 444 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 333 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 222 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 111 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 99 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 77 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 55 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 33 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 22 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 11 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 9 )
//    {
//      lcd.clear();
//    }
    lcd.print(voltage);
    lcd.setCursor(11, 0);
    lcd.print("V"); 
    
    //lcd.print(pwmspeed); //prints speed in bits
    Timer1.pwm(fanPin, pwmspeed); //output pwm per bits definition
    
    
    lcd.setCursor(0, 1);
    lcd.print("DutyCycle: ");
    lcd.setCursor(11, 1);
    lcd.print(cycle);
    lcd.setCursor(15, 1);
    lcd.print("%");    
    //delay(250);
    
//     if ( pwmspeed == 999 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 905 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 951 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 888 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 844 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 777 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 666 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 555 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 444 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 333 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 222 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 111 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 99 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 77 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 55 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 33 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 22 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 11 )
//    {
//      lcd.clear();
//    }
//    if ( pwmspeed == 9 )
//    {
//      lcd.clear();
//    }

 
}


