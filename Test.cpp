#include <iostream>
#include <string>
#include <sstream>

int main() {
    std::string s = "den=1, dieuhoa=0";
    int den = 0, dieuhoa = 0;

    // Replace commas with spaces to simplify parsing
    for (char& ch : s) {
        if (ch == ',' || ch == '=') {
            ch = ' ';
        }
    }

    std::istringstream ss(s);
    std::string temp;
    while (ss >> temp) {
        if (temp == "den") {
            ss >> den;
        } else if (temp == "dieuhoa") {
            ss >> dieuhoa;
        }
    }

    std::cout << "den = " << den << ", dieuhoa = " << dieuhoa << std::endl;
    return 0;
}
