# Onelinerizer
A simple tool to convert a multiline code to a single line

### Description
The main purpose was to get more familiar with python bytecode as well as trying to implement 
a simple virtual machine, decompiler and a onelinerizer

### Dependencies
No dependencies, however the python version should be 3.11.0 or any with compatible bytecode

### Limitations
- Classes and functions are not supported
- All "projects" can work with a limited subset of python code
- Code must have `main()` function and all code should be written in it, including imports
- `main()` must have `return` at the end

### Example
Onelinerizer turns this:
```python
def main():
    a = 1
    b = 2
    print(a + b)

    return


if __name__ == '__main__':
    main()
```
into this:
```python
(lambda: [(lambda a: [(lambda b: [print((a + b)), None, ][-1])(2)][-1])(1)][-1])()
```

### Acknowledgments
- The main inspiration was [onelinerizer for python2](https://github.com/csvoss/onelinerizer)
- Python docs [link](https://docs.python.org/3/library/dis.html#dis.get_instructions)
- Python bytecode docs [link](https://pl.python.org/docs/lib/bytecodes.html)
- Old article which wasn't really useful, but it was interesting to read 
[On writing Python one-liners](http://blog.sigfpe.com/2008/09/on-writing-python-one-liners.html)
