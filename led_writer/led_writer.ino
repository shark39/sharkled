#include <FastLED.h>

#define LED_PIN     5
#define NUM_LEDS    150
#define BRIGHTNESS  80
#define LED_TYPE    WS2812
#define COLOR_ORDER GRB
CRGB leds[NUM_LEDS];

#define UPDATES_PER_SECOND 1000


void setup() {
  
    delay( 3000 ); // power-up safety delay
    FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
    FastLED.setBrightness(  BRIGHTNESS );
    Serial.begin(9600);
    
}

void loop() {
  while (Serial.available() > 0) {
    int pos = Serial.parseInt();
    int r = Serial.parseInt();
    int g = Serial.parseInt();
    int b = Serial.parseInt();
    Serial.print(r);
    leds[pos].r = r;//Serial.parseInt();
    leds[pos].g = g;//Serial.parseInt();
    leds[pos].b = b;//Serial.parseInt();
  }
  FastLED.show();
  FastLED.delay(1000 / UPDATES_PER_SECOND);
}
