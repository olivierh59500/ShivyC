int main() {
  // error: variable of void type declared
  void a;

  // error: missing identifier name in declaration
  int *;

  // error: unrecognized set of type specifiers
  int int a;

  // error: unrecognized set of type specifiers
  unsigned signed int a;

  // error: extern variable has initializer
  extern int a = 10;

  // error: too many storage classes in declaration specifiers
  extern auto int b;

  {
    int c;
  }
  // error: use of undeclared identifier 'c'
  c;
}
