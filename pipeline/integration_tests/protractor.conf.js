var ab = require('asyncblock');
var config = require('../config.js');

function buildSuitePath(name) {
  return '../../build/test/test/e2e/uia/spec/**/*' + name + '*_test.js'
}

// protractor configuration file (see options doc at https://github.com/angular/protractor/blob/master/docs/referenceConf.js)
exports.config = {
  seleniumAddress: 'http://localhost:9515',

  // ----- What tests to run -----

  specs: ['../../build/develop/test/spec/**/*_test.js'],

  suites: {

  },

  // ----- More information for your tests ----

  onPrepare: function (){
    ab.enableTransform();

    // The require statement must be down here, since jasmine-reporters
    // needs jasmine to be in the global and protractor does not guarantee
    // this until inside the onPrepare function.
    var jasmineReporters = require('jasmine-reporters');
    jasmine.getEnv().addReporter(
      // junit reporter for build server
      new jasmineReporters.JUnitXmlReporter({
        savePath: '/tmp/lambda_protractor/build/test/test/e2e/results',
        filePrefix: 'junitresults-' + Math.floor(Math.random() * 999999999999), //When there are multiple shards, each needs to write to a unique file
        consolidate: true,
        modifySuiteName: function(generatedSuiteName, suite) {
          return 'E2E.' + generatedSuiteName;
        },
        useDotNotation: true
      })
    );

    var jasmineSpecReporter = require('jasmine-spec-reporter');
    jasmine.getEnv().addReporter(
      // console reporter for running tests locally
      new jasmineSpecReporter({ displayStacktrace: 'all' })
    );

    const allureJsCommons = require('allure2-js-commons');
    const allureJasmine = require('jasmine-allure2-reporter');

    const runtime = new allureJsCommons.AllureRuntime({
      resultsDir: '/tmp/lambda_protractor/build/test/test/e2e/allure-results',
      testMapper: (result) => {
        return result;
      }
    });

    const reporter = new allureJasmine.JasmineAllureReporter(runtime);
    jasmine.getEnv().addReporter(reporter);

    const allure = reporter.getInterface();
    jasmine.getEnv().afterEach((done) => {
      browser.takeScreenshot().then((png) => {
        allure.attachment('Screenshot', new Buffer(png, 'base64'), 'image/png');
        done();
      }).catch((e) => {
        console.log(`Failed to capture screenshot: ${e.message}`);
        done();
      });
    });

    const Status = allureJsCommons.Status;
    runtime.writeCategories([
      {
        "name": "Exception",
        "messageRegex": ".*\\sException:.*",
        "matchedStatuses": [
          Status.BROKEN
        ]
      }
    ]);

    browser.manage().timeouts().pageLoadTimeout(30000);
    browser.ignoreSynchronization = true;
    
  },

  // ----- The test framework -----

  framework: 'jasmine2',

  // Options to be passed to minijasminenode.
  jasmineNodeOpts: {
    // If true, print colors to the terminal.
    showColors: true,
    // Default time to wait in ms before a test fails.
    defaultTimeoutInterval: 9000000,
    // remove protractor dot reporter; we are using a custom reporter instead
    print: function() {}
  },

  capabilities: {
    browserName: 'chrome',
    chromeOptions: {
      args: [ 
      '--disable-gpu',
      '--single-process',
      '--no-sandbox',
      '--data-path=/tmp/data-path',
      '--homedir=/tmp/homedir',
      '--disk-cache-dir=/tmp',
      '--disk-cache-size=1',
      '--media-cache-size=1',
      '--allow-file-access-from-files',
      '--enable-logging',
      '--v=1',
      '--disable-web-security',
      '--disable-extensions',
      '--ignore-certificate-errors',
      '--disable-ntp-most-likely-favicons-from-server',
      '--disable-ntp-popular-sites',
      '--window-size=1366,1024', 
      '--disable-infobars',
      '--disable-dev-shm-usage',
      'enable-precise-memory-info'
    ],
      binary: '/tmp/chrome-lambda/chrome',
      prefs: {
        'credentials_enable_service': false,
        'profile': {
          'password_manager_enabled': false
        }
      }
    }
  },
};
