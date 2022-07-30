#include <SoftwareSerial.h>

#include <Servo.h>

// Servor Motor setup
const int num_of_servos = 6;
int pin[num_of_servos] = {11, 12, 13, 10, 9, 8};
Servo servos[num_of_servos];
int min_pwm[num_of_servos] = {600, 1500, 1150, 500, 500, 800};
int max_pwm[num_of_servos] = {2400, 2400, 1950, 2500, 2500, 1700};
int home_pwm[num_of_servos] = {1400, 2008, 1527, 1465, 2072, 800};
int squeeze_pwm[num_of_servos];
int span_pwm[num_of_servos];
int last_pwm[num_of_servos];
int current_pwm[num_of_servos];
int target_pwm[num_of_servos];
int accel[num_of_servos] = {5,8,5, 5, 5, 1};
bool set_last_pwm[num_of_servos] = {true, true, true, true, true, true};
//time delay
int time_delay = 150;

//serial paparms
const byte numChars = 32;
char receivedChars[numChars];
String command = "Start";
int received_pwd = 0;
int received_joint = 0;

boolean newData = false;

//print setup
boolean print_once = 1;

void setup(){
  Serial.begin(9600);
  
  for(int i=0; i<num_of_servos; i++){
     servos[i].attach(pin[i]);
  }

  reset();

  Serial.println("<Arduino is ready>");
  print_();
  delay(2000);                       
}

void loop() {
  recvWithStartEndMarkers();
  myStrtok();
  parseSerialBuffer();
  setCurrentPwm();
  //avoidCollision();

  run_();
  setLastPwm();
  print_();
  delay(time_delay);
}

void avoidCollision(){
  for(int i=0;i<num_of_servos;i++)
    current_pwm[i] = checkPwmBoundry(current_pwm[i], min_pwm[received_joint], max_pwm[received_joint]);
}
void parseSerialBuffer() {

  if(command == "runsp"){
      target_pwm[received_joint] = checkPwmBoundry(received_pwd, min_pwm[received_joint], max_pwm[received_joint]);
      print_once=1;
   }
   else if(command == "run"){
      target_pwm[received_joint] = checkPwmBoundry(received_pwd, min_pwm[received_joint], max_pwm[received_joint]);
      set_last_pwm[received_joint] = false;
      print_once=1;
   }
   else if(command == "runh"){
    runHome();
    print_once=1;
   }
   else if(command == "runs"){
    runSpan();
    print_once=1;
   }
   else if(command == "runsq"){
    runSqueeze();
    print_once=1;
   }
   else if(command == "runmin"){
    runMin();
    print_once=1;
   }
   else if(command == "runmax"){
    runMax();
    print_once=1;
   }
   else if(command == "runrnd"){
    runRand();
    print_once=1;
   }
   else if (command == "print"){
      print_once=1;
  }
  else if(command == "delay"){
    time_delay = received_pwd;
    print_once=1;
  }
  else if(command == "min"){
    min_pwm[received_joint] = received_pwd;
    print_once=1;
   }
   else if(command == "max"){
      max_pwm[received_joint] = received_pwd;
      print_once=1;
   }
   else if(command == "home"){
      home_pwm[received_joint] = received_pwd;
      print_once=1;
   }
   else if(command == "reset"){
      reset();
      print_once=1;
   }
}

void print_(){
  if(print_once==1){
    print_once = 0;
    //Serial.println("<-------------Print servos state-------------");
    Serial.println("<");
    for(int i=0;i<num_of_servos;i++){
      Serial.print("Servo ");
      Serial.print(i);
      Serial.print(" pos: ");
      Serial.print(last_pwm[i]);
      Serial.print(" | ");
      Serial.print(current_pwm[i]);
      Serial.print(" | ");
      Serial.println(target_pwm[i]);
    }
    /*for(int i=0;i<num_of_servos;i++){
      Serial.print("Servo ");
      Serial.print(i);
      Serial.print(" set_last_pwm: ");
      Serial.println(set_last_pwm[i]);
    }
    for(int i=0;i<num_of_servos;i++){
      Serial.print("Servo ");
      Serial.print(i);
      Serial.print(" accel: ");
      Serial.println(accel[i]);
    }
    Serial.print("time_delay: ");
    Serial.println(time_delay);
    Serial.print("command: ");
    Serial.println(command);
    Serial.print("recived_joint: ");
    Serial.println(received_joint);
    Serial.print("received_pwd: ");
    Serial.println(received_pwd);*/
    Serial.println(">");
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

void runHome(){
  for(int i=0;i<num_of_servos;i++){
    target_pwm[i] = home_pwm[i];
    set_last_pwm[i] = false;
  }
}
void runRand(){
  for(int i=0;i<num_of_servos;i++){
    target_pwm[i] = random(min_pwm[i], max_pwm[i]);
    set_last_pwm[i] = false;
  }
}
void runSqueeze(){
  for(int i=0;i<num_of_servos;i++){
    target_pwm[i] = squeeze_pwm[i];
    set_last_pwm[i] = false;
  }
}
void runSpan(){
  for(int i=0;i<num_of_servos;i++){
    target_pwm[i] = span_pwm[i];
    set_last_pwm[i] = false;
  }
}

void runMax(){
  for(int i=1;i<num_of_servos;i++){
    target_pwm[i] = max_pwm[i];
    set_last_pwm[i] = false;
  }
}

void runMin(){
  for(int i=1;i<num_of_servos;i++){
    target_pwm[i] = min_pwm[i];
    set_last_pwm[i] = false;
  }
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
      current_pwm[i] = checkPwmBoundry(current_pwm[i], min_pwm[i], max_pwm[i]);
    }
  }
  
}

int checkPwmBoundry(int pwm, int min_pwm, int max_pwm){
  if(pwm<min_pwm){
    Serial.print("<Warning, pwm is out of min boundry: ");
    Serial.print(min_pwm);
    Serial.print(" | ");
    Serial.println(pwm);
    Serial.println(">");
    pwm = min_pwm;
  }
  if(pwm>max_pwm){
    Serial.print("<Warning, pwm is out of max boundry: ");
    Serial.print(max_pwm);
    Serial.print(" | ");
    Serial.println(pwm); 
    pwm = max_pwm;  
    Serial.println(pwm);
    Serial.println(">");
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

void myStrtok (){
  const char *delimiter = ":";
  int ind=0;
  int num[3];
  command = "";
  if (newData == true) {
    char* d = strtok(receivedChars, delimiter);
    command = String((char *)d);
    while (d != NULL) {
        num[ind] = atoi(d);
        ind++;
        d = strtok(NULL, delimiter);
    }
    newData = false;
    if(ind==3){
      received_joint = num[1];
      received_pwd = num[2];
      if(received_joint<0 | received_joint>=num_of_servos){
        Serial.print("<Recived joint is out off bondry: ");
        Serial.println(received_joint);
        Serial.println(">");
        received_joint = 0;
      }
    }
    else if(ind==2){received_pwd = num[1];}
    else if(ind==1){Serial.print("<Warning: Inserted command only: ");Serial.print(command);Serial.println(">");}
    else if(ind == 0){Serial.println("<Error: Invalid input, missing right delimiter>");}
  }
}
