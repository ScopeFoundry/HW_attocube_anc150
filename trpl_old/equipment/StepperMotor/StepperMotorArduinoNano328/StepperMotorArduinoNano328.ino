/*
Controll stepper motor in combinaiton with a Pololu - A4988 Stepper Motor Driver Carrier
Serial commands examples:
  'S100' makes 100 stepps in one direchtion; 'S-38' makes 38 stepps in the other direction; Stopp the motor with 'S0';
  'T23' sets the pulse length to 2 * 23 milliseconds (23 ms HIGH and 23 ms LOW). Default is T20.
09/21/2014 Benedikt Ursprung 
*/
int steppPin = 11;
int dirPin = 12;
int sleepPin = 10;

int steppsToDo;
int steppsDone;
int tPulse;
boolean Direction;

void setup() {
  // initialize serial:
  Serial.begin(9600);
    while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }

  steppsToDo=0;
  steppsDone=0;
  tPulse=5;
  Direction = false;
  pinMode(steppPin, OUTPUT); 
  pinMode(dirPin, OUTPUT); 
  pinMode(sleepPin, OUTPUT); 

  digitalWrite(dirPin, Direction); 

  digitalWrite(sleepPin,HIGH);
  
  for(int i=0; i<100; i++){
     makeStepp(); 
  }

  Direction = true;
  digitalWrite(dirPin, Direction); 
  
  for(int i=0; i<100; i++){
     makeStepp(); 
  }

  digitalWrite(sleepPin,LOW);
  

  //digitalWrite(sleepPin,LOW);
}


void loop() {

  serialEvent();
  if(steppsToDo>steppsDone){
    makeStepp();
    steppsDone++;
    //Serial.print("SteppsToDo= "); 
    //Serial.println(steppsToDo); 
    //Serial.print("SteppsDone= "); 
    //Serial.println(steppsDone);  
     
  }
  else{
    digitalWrite(sleepPin,LOW);
    delay(200);
  }
    



}


void makeStepp(){
  digitalWrite(steppPin, HIGH); 
  delay(tPulse);
  digitalWrite(steppPin, LOW);    
  delay(tPulse);
}  
  


void serialEvent(){
  if(Serial.available()) {
    Serial.print('R');
    char cmd = (char)Serial.read();
    int inputNumber = Serial.parseInt();
    Serial.print(cmd);
    Serial.println(inputNumber);

    if(cmd == 'S'){
      digitalWrite(sleepPin,HIGH);

      boolean newDirection;
      if (inputNumber<0){
        
        newDirection = HIGH;
        inputNumber = -inputNumber;
      }
      else{
        newDirection = LOW;
      }
      if(newDirection!=Direction){
        Direction = newDirection;
        digitalWrite(dirPin, Direction); 
        delay(10);        
      }

      steppsToDo = inputNumber;
      steppsDone = 0;
      
    }
    else if(cmd == 'T'){

      tPulse = inputNumber;
      //Serial.print("tPulse:");
      //Serial.println(tPulse);     

    }
  }
}









