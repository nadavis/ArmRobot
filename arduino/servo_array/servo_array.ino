#include <SoftwareSerial.h>

#include <Servo.h>

// Servor Motor setup
const int num_of_servos = 6;
int pin[num_of_servos] = {11, 12, 13, 10, 9, 8};
Servo servos[num_of_servos];
int min_pwm[num_of_servos] = {600, 1500, 1150, 500, 500, 800};
int max_pwm[num_of_servos] = {2400, 2400, 1950, 2500, 2500, 1700};
int home_pwm[num_of_servos] = {1400, 2020, 1527, 1465, 2072, 800};
int squeeze_pwm[num_of_servos];
int span_pwm[num_of_servos];
int last_pwm[num_of_servos];
int current_pwm[num_of_servos];
int target_pwm[num_of_servos];
int accel[num_of_servos] = {5, 8, 5, 5, 5, 1};
bool set_last_pwm[num_of_servos] = {true, true, true, true, true, true};
//time delay
int time_delay = 150;

//serial paparms
const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars]; 
String messageFromPC = "Start";
boolean newData = false;

void setup(){
  Serial.begin(9600);
  
  for(int i=0; i<num_of_servos; i++){
     servos[i].attach(pin[i]);
  }

  reset();

  Serial.println("<Arduino is ready>");
  //print_();
  delay(2000);                       
}

void loop() {
  recvWithStartEndMarkers();
  parseSerialBuffer();
  setCurrentPwm();
  //avoidCollision();

  run_();
  setLastPwm();
  delay(time_delay);
}

void avoidCollision(){
  for(int i=0;i<num_of_servos;i++)
    current_pwm[i] = checkPwmBoundry(i, current_pwm[i], min_pwm[i], max_pwm[i]);
}

void print_(){
  //Serial.println("<-------------Print servos state-------------");
  for(int i=0;i<num_of_servos;i++){
    Serial.println("<Servo "+String(i)+" pos: "+String(last_pwm[i])+ " | "+String(current_pwm[i])+" | "+String(target_pwm[i])+">");
  }
}
void reset(){
  for(int i=0;i<num_of_servos;i++){
    target_pwm[i] = home_pwm[i];
    current_pwm[i] = home_pwm[i];
    last_pwm[i] = home_pwm[i];
    span_pwm[i] = home_pwm[i];
    squeeze_pwm[i] = max_pwm[i];
    set_last_pwm[i] = true;

  }
  span_pwm[1] = min_pwm[1]+200;
  squeeze_pwm[0] = home_pwm[0];
  squeeze_pwm[3] = home_pwm[3];
  squeeze_pwm[4] = min_pwm[4];
  squeeze_pwm[5] = home_pwm[5];

}

void run_(){
  for(int i=0; i<num_of_servos; i++){
    servos[i].writeMicroseconds(current_pwm[i]);
  }
}

void setLastPwm(){
  for(int i=0; i<num_of_servos; i++){
    if(current_pwm[i] == target_pwm[i]){
      set_last_pwm[i] = true;
    } if(set_last_pwm[i])
      last_pwm[i] = target_pwm[i];
  }
}

int sign(int value) {
  if(value>0){return 1;}
  else if(value<0){return -1;}
}
void setCurrentPwm(){
  int d;
  for(int i=0; i<num_of_servos; i++){
    if(set_last_pwm[i]){
      current_pwm[i] = target_pwm[i];
    }else{
      //d = (target_pwm[i] - last_pwm[i]) / accel[i];
      d = min(abs(target_pwm[i] - current_pwm[i]), abs(current_pwm[i] - last_pwm[i])) / accel[i]+1;
      if(target_pwm[i] >= last_pwm[i])
        current_pwm[i] = current_pwm[i] + d;
      else if(target_pwm[i] < last_pwm[i])
        current_pwm[i] = current_pwm[i] - d;
        
      if((current_pwm[i] >= target_pwm[i]) & (target_pwm[i] >= last_pwm[i])){
        current_pwm[i] = target_pwm[i];
      }else if((current_pwm[i] < target_pwm[i]) & (target_pwm[i] < last_pwm[i])){
        current_pwm[i] = target_pwm[i];
      }
      current_pwm[i] = checkPwmBoundry(i, current_pwm[i], min_pwm[i], max_pwm[i]);
    }
  }
}

int checkPwmBoundry(int i, int pwm, int min_pwm, int max_pwm){
  if(pwm<min_pwm){
    Serial.println("<Warning, Servo "+String(i) +" pwm is out of min boundry: "+String(min_pwm)+" | "+String(pwm)+">");
    pwm = min_pwm;
  }
  if(pwm>max_pwm){
    Serial.println("<Warning, pwm is out of max boundry: "+String(max_pwm)+" | "+String(pwm)+">");
    pwm = max_pwm;  
  }
  return pwm;
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

void parseSerialBuffer(){
  char * strtokIndx; 
  const char *delimiter = ":";
  messageFromPC = "";
  
  if (newData == true) {
    strcpy(tempChars, receivedChars);

    strtokIndx = strtok(tempChars, delimiter);  
    //strcpy(messageFromPC, strtokIndx); 
    messageFromPC = String((char *)strtokIndx);
    Serial.println("<msg: "+ messageFromPC + ">");
    if(messageFromPC == "run"){
      for(int i=0;i<num_of_servos-1;i++){
        strtokIndx = strtok(NULL, delimiter); 
        target_pwm[i] = atoi(strtokIndx);
        set_last_pwm[i] = false;
        Serial.println("<Run " + String(i) + "-" + String(target_pwm[i]) + ">");
      }
      //Serial.println("<Run g-"+String(target_pwm[num_of_servos-1])+">");
    }
    else if(messageFromPC == "gripper"){
      strtokIndx = strtok(NULL, delimiter); 
      target_pwm[num_of_servos-1] = atoi(strtokIndx);
      set_last_pwm[num_of_servos-1] = true;
      Serial.println("<Run g-"+String(target_pwm[num_of_servos-1])+">");
    }
    else if (messageFromPC == "print"){print_();}
    else{Serial.println("<Error: Incorrect command: "+messageFromPC+">");}
    newData = false;
  }
}
