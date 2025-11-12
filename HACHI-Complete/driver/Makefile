CXX := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -pedantic -O2
LDFLAGS := -lusb-1.0
TARGET := cosmos_bridge

all: $(TARGET)

$(TARGET): cosmos_bridge.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f $(TARGET)

.PHONY: all clean
