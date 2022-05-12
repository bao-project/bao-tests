# Table of contents
- [Test definition](#test-definition)
  * [Unit test](#unit-test)
  * [Test proprieties](#test-proprieties)
    + [Critical test](#critical-test)
    + [Long run test](#long-run-test)
    + [Test template](#test-template)
  * [Test suit](#test-suit)
  * [Test setup](#test-setup)
  * [Setup test directory](#setup-test-directory)

# Test definition
## Unit test
A unit test can be defined to evaluate a procedure (block of code).

## Test proprieties
For each test, the following parameters can be set:

### Critical test
- True - The test process should be stopped if the test fails
- False - The test process can continue even if the test fails

### Long run test
- True - The test duration is considered long (long-time run)
- False - The test is considered fast (short-time run

### Test template
A test definition must follow the outlined nomenclature.

```C
BAO_TEST(#suite_name, #test_name, #criticality, #long_run)
{
 // test code here
}
```

## Test suit
The term "test suite" refers to a group of tests. Grouping the tests enables a more organized selection of tests, making running numerous tests easier.

<table class="tg">
<thead>
  <tr>
    <th class="tg-c3ow">Suit name</th>
    <th class="tg-c3ow">Test name</th>
    <th class="tg-c3ow">Critical test</th>
    <th class="tg-c3ow">Long test</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td class="tg-c3ow" rowspan="3">Suit_1<br></td>
    <td class="tg-c3ow">Test_1</td>
    <td class="tg-c3ow">T/F</td>
    <td class="tg-c3ow">T/F</td>
  </tr>
  <tr>
    <td class="tg-c3ow">Test_2</td>
    <td class="tg-c3ow">T/F</td>
    <td class="tg-c3ow">T/F</td>
  </tr>
  <tr>
    <td class="tg-c3ow">Test_3</td>
    <td class="tg-c3ow">T/F</td>
    <td class="tg-c3ow">T/F</td>
  </tr>
  <tr>
    <td class="tg-c3ow" rowspan="3">Suit_2<br></td>
    <td class="tg-c3ow">Test_1</td>
    <td class="tg-c3ow">T/F</td>
    <td class="tg-c3ow">T/F</td>
  </tr>
  <tr>
    <td class="tg-c3ow">Test_2</td>
    <td class="tg-c3ow">T/F</td>
    <td class="tg-c3ow">T/F</td>
  </tr>
  <tr>
    <td class="tg-c3ow">Test_3</td>
    <td class="tg-c3ow">T/F</td>
    <td class="tg-c3ow">T/F</td>
  </tr>
</tbody>
</table>

## Test setup
In order to use Bao Test Framework you have go throught the following steps:

1. Add the following lines to your linkerscript
	```c
	.testframework : {
	    __testframework_start = . ;
	    *(.testframework.PRIO* .testframework.prio*)
	    *(.testframework.*)
	    __testframework_end = . ;        
	}
	```

2. Add the following lines to your makefile (use the variable TEST_DIR to indicate the directory where all the file containing tests are. The variable REPO_DIR should point to the base directory of this repository. Additionally, the variables names C_SRC, INC_DIRS, and CFLAGS may have to be modified according to your makefile.)

	```c
    TESTS_DIR:=$(SRC_DIR)/tests
    REPO_DIR:=$(SRC_DIR)/../bao-tests
    include bao-tests/src/bao-test.mk
    C_SRC += $(BAO_TEST_SRCS)
    INC_DIRS += $(BAO_TEST_INC_DIR)
    CFLAGS += $(BAO_TEST_FLAGS)
	```
(Note: If you are using the C library without the Python tool, make sure you add also delete the test build directory in your clean rule)

3. Add to your source the entry point (bao_test_entry()) to our framework, where you feel it is correct.
4. Create a .c file (or multiple) in the directory specified early, include bao_test.h and create tests according to the [test definition example](#Test template).
5. Build your system normally adding the following variable to your make command:

	```c
	BAO_TEST=1 -> mandatory to use the framework, otherwise no test will be executed
    SUITES="suite1 suite2" -> to specify which suites need to be executed
    TESTS="test1 test2" -> to specify which tests are to bexecuted
	```

## Setup test directory
The test platform directory provides a template of a VMM, a VM, and a Guest. These templates are available in the BAO_Test/ directory. A test relating to a MUT should be placed in that module's directory. Tests must be grouped into suits (directory name equals to the suit name) inside the module directory.

```c
BAO_Test/
├─ VMM_template
├─ VM_template
├─ VM_Test/
│  ├─ Suit_1/
│  │  ├─ Test_1
│  │  ├─ Test_n
│  ├─ Suit_n/
│  │  ├─ Test_1
│  │  ├─ Test_n
├─ VMM_Test/
├─ Guest_Test/	
```

