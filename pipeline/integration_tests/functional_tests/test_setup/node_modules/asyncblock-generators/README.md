```
                                        ______  ______              ______  
______ ______________  _________ __________  /_ ___  /______ __________  /__
_  __ `/__  ___/__  / / /__  __ \_  ___/__  __ \__  / _  __ \_  ___/__  //_/
/ /_/ / _(__  ) _  /_/ / _  / / // /__  _  /_/ /_  /  / /_/ // /__  _  ,<   
\__,_/  /____/  _\__, /  /_/ /_/ \___/  /_.___/ /_/   \____/ \___/  /_/|_|  
                /____/                                                      

```
==================================================================

A synchronous-style flow control library built on top of harmony generators. This library started its life as [asyncblock](https://github.com/scriby/asyncblock),
which was written on top of Fibers.

###Installation

```javascript
npm install asyncblock-generators
```

### Why should I use asyncblock?

* Write async code in synchronous style without blocking the event loop
* Effortlessly combine serial and parallel operations with minimal boilerplate
* Produce code which is easier to read, reason about, and modify
    * Compared to flow control libraries, asyncblock makes it easy to share data between async steps. There's no need to create variables in an outer scope or use "waterfall".
* Simplify error handling practices
    * If an error occurs in an async step, automatically call your callback with the error, or throw an Error
* Improve debugging by not losing stack traces across async calls
    * Line numbers don't change. What's in the stack trace maps directly to your code (You may lose this with CPS transforms)
    * If using a debugger, it's easy to step line-by-line through asyncblock code (compared to async libraries)

## Usage differences between this module and asyncblock

* All functions passed to an asyncblock must be generator functions (look like function*(){})
* Any time you are waiting on a value to resolve the "yield" keyword must be used
* There is a new shorthand for waiting on one item: `var x = yield fs.readFile(path, 'utf8', flow.callback());`
* When using source transformation, .defer() and .future() calls may only be yielded once. (This is probably fixable, but I haven't looked into it yet)
* asyncblock.getCurrentFiber() is not availabe in this module (this is not commonly used)

Cheat sheet for when yield must be used:

* `yield flow.wait();`
* `yield flow.get('key');`
* `yield flow.sync(setTimeout(flow.add(), 1000);`
* `yield fs.readFile(path, 'utf8', flow.callback())`
* `yield fs.readFile(path, 'utf8').sync()`
* `var x = fs.readFile(path, 'utf8').defer(); console.log(yield x)`
* `var x = fs.readFile(path, 'utf8').future(); console.log(yield x.result)`

This library is unable to detect it if you accidentally forget to include a yield keyword. Please pay close attention to including it when necessary.

## Overview

Check out the [overview](https://github.com/scriby/asyncblock/blob/master/docs/overview.md) to get an at-a-glance overview
of the different ways asyncblock can be used. Please note that the docs are for the fibers version of asyncblock, and the examples
will need to be translated to include * and yields for the generator version.

## Examples

A few quick examples to show off the functionality of asyncblock:

### Sleeping in series

```javascript
var ab = require('asyncblock-generators');

ab(function*(flow){
    console.time('time');

    setTimeout(flow.add(), 1000);
    yield flow.wait(); //Wait for the first setTimeout to finish

    setTimeout(flow.add(), 2000);
    yield flow.wait(); //Wait for the second setTimeout to finish

    console.timeEnd('time'); //3 seconds
});
```

### Sleeping in parallel

```javascript
var ab = require('asyncblock-generators');

ab(function*(flow){
    console.time('time');

    setTimeout(flow.add(), 1000);
    setTimeout(flow.add(), 2000);
    yield flow.wait(); //Wait for both setTimeouts to finish

    console.timeEnd('time'); //2 seconds
});
```

### Trapping results

```javascript
var ab = require('asyncblock-generators');

ab(function*(flow) {
    //Start two parallel file reads
    fs.readFile(path1, 'utf8', flow.set('contents1'));
    fs.readFile(path2, 'utf8', flow.set('contents2'));
    
    //Print the concatenation of the results when both reads are finished
    console.log(yield flow.get('contents1') + yield flow.get('contents2'));
    
    //Wait for a large number of tasks
    for(var i = 0; i < 100; i++){
        //Add each task in parallel with i as the key
        fs.readFile(paths[i], 'utf8', flow.add(i));                                    
    }
    
    //Wait for all the tasks to finish. Results is an object of the form {key1: value1, key2: value2, ...}
    var results = yield flow.wait();
    
    //One-liner syntax for waiting on a single task
    var contents = yield fs.readFile(path, 'utf8', flow.callback());


    //See overview & API docs for more extensive description of techniques
});
```

### With source transformation

```javascript
//asyncblock.enableTransform() must be called before requiring modules using this syntax.
//See overview / API for more details

var ab = require('asyncblock-generators');

if (ab.enableTransform(module)) { return; }

ab(function*(flow) {
    //Start two parallel file reads
    var contents1 = fs.readFile(path1, 'utf8').defer();
    var contents2 = fs.readFile(path2, 'utf8').defer();
    
    //Print the concatenation of the results when both reads are finished
    console.log(yield contents1 + yield contents2);
    
    var files = [];
    //Wait for a large number of tasks
    for(var i = 0; i < 100; i++){
        //Add each task in parallel with i as the key
        files.push( fs.readFile(paths[i], 'utf8').future() );
    }
    
    //Get an array containing the file read results
    var results = files.map(function(future){
        return yield future.result;
    });
    
    //One-liner syntax for waiting on a single task
    var contents = yield fs.readFile(path, 'utf8').sync();
    
    //See overview & API docs for more extensive description of techniques
});
```

### Returning results and Error Handling

```javascript
var ab = require('asyncblock-generators');

if (ab.enableTransform(module)) { return; }

var asyncTask = function(callback) {
    ab(function*(flow) {
        var contents = yield fs.readFile(path, 'utf8').sync(); //If readFile encountered an error, it would automatically get passed to the callback

        return contents; //Return the value you want to be passed to the callback
    }, callback); //The callback can be specified as the 2nd arg to asyncblock. It will be called with the value returned from the asyncblock as the 2nd arg.
                  //If an error occurs, the callback will be called with the error as the first argument.
});
```

## API

See [API documentation](https://github.com/scriby/asyncblock/blob/master/docs/api.md)

## Stack traces

See [stack trace documentation](https://github.com/scriby/asyncblock/blob/master/docs/stacktrace.md)

## Error handling

See [error handling documentation](https://github.com/scriby/asyncblock/blob/master/docs/errors.md)

## Formatting results

See [formatting results documentation](https://github.com/scriby/asyncblock/blob/master/docs/results.md)

## Parallel task rate limiting

See [maxParallel documentation](https://github.com/scriby/asyncblock/blob/master/docs/maxparallel.md)

## Task timeouts

See [timeout documentation](https://github.com/scriby/asyncblock/blob/master/docs/timeout.md)

## Concurrency

Both generators, and this module, do not increase concurrency in nodejs. There is still only one thread executing at a time.
Generators are like threads which are allowed to pause and resume where they left off without blocking the event loop.

## Risks

* Generators are fast, but they're not the fastest. CPU intensive tasks may prefer other solutions (you probably don't want to do CPU intensive work in node anyway...)

## Compared to other solutions...

A sample program in pure node, using the async library, and using asyncblock-generators.

### Pure node

```javascript

function example(callback){
    var finishedCount = 0;
    var fileContents = [];

    var continuation = function(){
        if(finishedCount < 2){
            return;
        }

        fs.writeFile('path3', fileContents[0] + fileContents[1], function(err) {
            if(err) {
                throw new Error(err);
            }

            fs.readFile('path3', 'utf8', function(err, data){ 
                console.log(data);
                console.log('all done');
            });
        });
    };

    fs.readFile('path1', 'utf8', function(err, data) {
        if(err) {
            throw new Error(err);
        }

        fnishedCount++;
        fileContents[0] = data;

        continuation();
    });

    fs.readFile('path2', 'utf8', function(err, data) {
        if(err) {
            throw new Error(err);
        }

        fnishedCount++;
        fileContents[1] = data;

        continuation();
    });
}
```

### Using async

```javascript

var async = require('async');

var fileContents = [];

async.series([
    function(callback){
        async.parallel([
            function(callback) {
                fs.readFile('path1', 'utf8', callback);
            },

            function(callback) {
                fs.readFile('path2', 'utf8', callback);
            }
        ],
            function(err, results){
                fileContents = results;                                    
                callback(err);
            }
        );
    },

    function(callback) {
        fs.writeFile('path3', fileContents[0] + fileContents[1], callback);
    },

    function(callback) {
        fs.readFile('path3', 'utf8', function(err, data){
            console.log(data);
            callback(err);
        });
    }
],
    function(err) {
        if(err) {
            throw new Error(err);
        }
        
        console.log('all done');
    }
);
```

### Using asyncblock-generators

```javascript
var ab = require('asyncblock-generators');

ab(function*(flow){
    fs.readFile('path1', 'utf8', flow.add('first'));
    fs.readFile('path2', 'utf8', flow.add('second'));
    
    //Wait until done reading the first and second files, then write them to another file
    fs.writeFile('path3', yield flow.wait('first') + yield flow.wait('second'), flow.add());
    yield flow.wait(); //Wait on all outstanding tasks

    fs.readFile('path3', 'utf8', flow.add('data'));

    console.log(yield flow.wait('data')); //Print the 3rd file's data
    console.log('all done');
});
```

### Using asyncblock + source transformation

```javascript
//Requires asyncblock.enableTransform to be called before requiring this module
var ab = require('asyncblock-generators');

if (ab.enableTransform(module)) { return; }

ab(function*(flow){
    var first = fs.readFile('path1', 'utf8').defer();
    var second = fs.readFile('path2', 'utf8').defer();
    
    fs.writeFile('path3', yield first + yield second).sync();

    var third = fs.readFile('path3', 'utf8').defer();

    console.log(yield third);
    console.log('all done');
});
```

### No prototypes were harmed in the making of this module