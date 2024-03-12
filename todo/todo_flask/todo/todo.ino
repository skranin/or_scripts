#include <Mouse.h>
#include <Keyboard.h>
#include <KeyboardLayout.h>
#include <SPI.h>
#include <HttpClient.h>
#include <Ethernet.h>
#include <EthernetClient.h>

// Button is connected to pin 7
#define BUTTON_PIN 7
// Led is conected to pin 8
#define LED_PIN_ON_OFF 8
// Print logs to the serial
#define LOG 1

// Name of the server we want to connect to
const char kHostname[] = "10.0.0.120";
// Port of the server we want to connect to
uint16_t port = 8088;
// Mac address of the arduino eth board
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };

// Number of milliseconds to wait without receiving any data before we give up
const int kNetworkTimeout = 30*1000;
// Number of milliseconds to wait if no data is available before trying again
const int kNetworkDelay = 1000;

static unsigned long ALT_TAB_REPEAT_INTERVAL = 10000; // ms
static unsigned long lastAltTabRefreshTime = 0;
	
static unsigned long MOUSE_RIGHT_CLICK_REPEAT_INTERVAL = 10000; // ms
static unsigned long lastMouseRighClickRefreshTime = 0;

byte lastButtonState = LOW;
byte ledOnOffState = LOW;

String ledStateString = "";
unsigned long debounceDuration = 50; // millis
unsigned long lastTimeButtonStateChanged = 0;

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN_ON_OFF, OUTPUT);
  //pinMode(LED_PIN_2, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP); //Use INPUT_PULLUP here, to enable embeded to the prototype board pull up resistor
  Mouse.begin();
  Keyboard.begin();
  // initialize serial communication:
  
  while (Ethernet.begin(mac) != 1)
  {
    log("Error getting IP address via DHCP, trying again...");
    delay(15000);
  }  
  delay(1000);
  log("DHCP assigned IP");
  Serial.println(Ethernet.localIP());

  // Using interrupt to monitor button separately from the main loop
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), buttonMonitor, CHANGE);
}

String get(char *url){
  int err =0;
  String result = "";
  EthernetClient c;
  HttpClient http(c);
  
  err = http.get(kHostname, port, url);
  if (err == 0)
  {


    err = http.responseStatusCode();
    if (err >= 0)
    {
      err = http.skipResponseHeaders();
      if (err >= 0)
      {
        int bodyLen = http.contentLength();
      
        unsigned long timeoutStart = millis();
        char c;
        while ( (http.connected() || http.available()) &&
               ((millis() - timeoutStart) < kNetworkTimeout) )
        {
            if (http.available())
            {
                c = http.read();
                result=result+c;
               
                bodyLen--;
                timeoutStart = millis();
            }
            else
            {
                delay(kNetworkDelay);
            }
        }
      }
      else
      {
        Serial.print("Failed to skip response headers: ");
        log(err);
      }
    }
    else
    {    
      Serial.print("Getting response failed: ");
      log(err);
    }
  }
  else
  {
    log("Connect failed: "+err);
  }
  http.stop();
  return result;
}

void loop() {
  if (ledOnOffState == HIGH) {
    // Clicking altTAB every x minutes here
    if(millis() - lastAltTabRefreshTime >= ALT_TAB_REPEAT_INTERVAL){
        ALT_TAB_REPEAT_INTERVAL = 1000*random(60,600);
        log("Nex time Alt will be pressed in " + String(ALT_TAB_REPEAT_INTERVAL/1000)+ " seconds");
		    lastAltTabRefreshTime = millis() ;
        altTab();

        log(get("/get-window"));
	  }
    // Clicking right mouse button every x minutes here
    if(millis() - lastMouseRighClickRefreshTime >= MOUSE_RIGHT_CLICK_REPEAT_INTERVAL){
        MOUSE_RIGHT_CLICK_REPEAT_INTERVAL = 1000*random(60,600);
        log("Next time mouse right click will be clicked " + String(MOUSE_RIGHT_CLICK_REPEAT_INTERVAL/1000)+ " seconds");
		    lastMouseRighClickRefreshTime = millis() ;
        altTab();
	  }
    MouseMoveRandom();
    delay(1000 * random(1, 30));
    typeSomeRandomKeys();
  }
}

void typeSomeRandomKeys(){
  // Typing some not-printable characters here.
  int keys[] = {KEY_PAGE_UP, KEY_PAGE_DOWN, KEY_UP_ARROW, KEY_DOWN_ARROW, KEY_LEFT_ARROW, KEY_RIGHT_ARROW};
  for(int i = 0; i <= random(1,7); i++)
  {
   int randomKeyElement = keys[random(0,5)];
   log("Clicking " + String(randomKeyElement) + " key");
   Keyboard.press(randomKeyElement);
   delay(10 * random(1, 5));
   Keyboard.releaseAll(); 
   delay(300 * random(1, 5));
  } 
  esc();
}

void altTab() {
  // Sends ALT+TAB multiple times (random)
  Keyboard.press(KEY_LEFT_ALT); 
  delay(100);
  // Clicking TAB few random times here
  int timesToClick = random(1, 5);
  log("Clicking ALT+TAB " + String(timesToClick) + " times.");
  for (int i = 0; i <= timesToClick; i++) {
    Keyboard.press(KEY_TAB);
    delay(random(100, 150));
    Keyboard.release(KEY_TAB); 
    delay(random(100, 150));
  }         
  Keyboard.releaseAll(); 
}

void esc(){
  // Sends ESC
  log("Sending ESC");
  Keyboard.press(KEY_ESC); 
  delay(random(100, 150));
  Keyboard.releaseAll(); 
}

void realType(String text){
  // Typing character by character here to be more human-like
  log("Typing " + text);
  for(auto x : text)
  {
    Keyboard.write(x);
    //Some random delay between characters
    delay(100 * random(1, 5));
  }
}

void MouseMoveRandom(){
  // Moves mouse to new position relative to current position
  log("Moving mouse");
  Mouse.move(random(-200, 200), random(-200,200));
}

void MouseRightClick(){
  log("Mouse right click");
  Mouse.click(MOUSE_RIGHT);
  delay(100 * random(10, 20));
  esc();
}

void buttonMonitor(){
  if (millis() - lastTimeButtonStateChanged > debounceDuration) {
    byte buttonState = digitalRead(BUTTON_PIN);
    if (buttonState != lastButtonState) {
      lastTimeButtonStateChanged = millis();
      lastButtonState = buttonState;
      if (buttonState == LOW) {
        ledOnOffState = (ledOnOffState == HIGH) ? LOW: HIGH;
        ledStateString = (ledOnOffState == HIGH) ? "ON": "Off";
        digitalWrite(LED_PIN_ON_OFF, ledOnOffState);
        log("Button pressed, script is " + ledStateString);
      }
    }
  }
}

void log(String text){
  if( LOG ==1){
    Serial.println(text);
  }
}