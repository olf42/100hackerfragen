/*
  Keyboard Message test

  For the Arduino Leonardo and Micro.

  Sends a text string when a button is pressed.

  The circuit:
   pushbutton attached from pin 4 to +5V
   10-kilohm resistor attached from pin 4 to ground

  created 24 Oct 2011
  modified 27 Mar 2012
  by Tom Igoe
  modified 11 Nov 2013
  by Scott Fitzgerald

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/KeyboardMessage
*/

#include "Keyboard.h"

const int buttonPinA = 11;          // input pin for pushbutton
const int buttonPinB = 9;
unsigned long lastpress;
int buttonStateA;
int buttonStateB;
bool is_pressed;


void setup() {
  // make the pushButton pin an input:
  pinMode(buttonPinA, INPUT);
  pinMode(buttonPinB, INPUT);
  // initialize control over the keyboard:
  Keyboard.begin(); 
}

void loop() {
  buttonStateA = digitalRead(buttonPinA);
  buttonStateB = digitalRead(buttonPinB);
  if (!buttonStateA && !buttonStateB) {
    is_pressed = false;
  }

  if ((millis() - lastpress < 1000) || is_pressed) {
     return;
  }

  if (buttonStateA && buttonStateB) {
    lastpress = millis();
    Keyboard.print('C');
    is_pressed = true;
  } else if (buttonStateA) {
    lastpress = millis();  
    Keyboard.print('A');
    is_pressed = true;
  } else if (buttonStateB) {
    lastpress = millis();  
    Keyboard.print('B');  
    is_pressed = true;
  }
}
