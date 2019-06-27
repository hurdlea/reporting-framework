# Example C++ Ion Writer 
This is an implementation of the Amazon Ion binary format that only only caters to the requirements of the Foxtel reporting specification. Together with the structure of the Python reporting toolkit structure this can be used as a basis for a full specification implementation.

## Files

*  reporting.cpp/h
*  ion_binary_writer.cpp/h
*  reporting_symbols.h

### reporting.cpp/h
This main class demonstrates the use of the ion_binary_writer functionality to implement the Foxtel reporting spec. It is a partial implementation of the Reporting header and Power Status event that writes a fixed test.10n file. Using the jsonify_ion.py script it is possible to view the ion binary output and validate a correctly formatted file. 

Note: The code does not attempt to deallocate memory to ensure proper operation when used in a long running process.  

### ion_binary_writer.cpp/h
This is a set of classes that implement most of the Amazon Ion base formats. The blob type is missing but is exceedingly similar to the string type. The string type should be fully UTF-8 compliant but the code as it stands does not cater for multi-byte code points.

### reporting_symbols
The header file defines the symbol table identifiers as described in the Foxtel specification. 

