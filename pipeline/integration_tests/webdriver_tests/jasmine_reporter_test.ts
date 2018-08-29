import * as ab from 'asyncblock';
import * as fs from 'fs';
import {browserSync, ElementFinderSync, elementSync} from '../../app';
import * as protractorSync from '../../app/index';
import path = require('path');

protractorSync.configure({implicitWaitMs: 500});

const TEST_AREA_ID = 'protractor_sync-test-area';

interface IAppendTestAreaOptions {
    style?: { [name: string]: string; };
    innerHtml?: string;
}

function appendTestArea(options?: IAppendTestAreaOptions) {
    browserSync.executeScript((id: string, _options?: IAppendTestAreaOptions) => {
        const existing = document.querySelector('#' + id);
        if (existing) {
            existing.parentNode.removeChild(existing);
        }

        const testArea = document.createElement('div');
        testArea.setAttribute('id', id);

        if (_options && _options.innerHtml) {
            testArea.innerHTML = _options.innerHtml;
        }

        if (_options && _options.style) {
            Object.keys(_options.style).forEach((item) => {
                (<any>testArea.style)[item] = _options.style[item];
            });
        }

        document.body.appendChild(testArea);
    }, TEST_AREA_ID, options);
}

function createTest(fn: Function, errorMsg?: string) {
    return (done: Function) => {
        ab(() => {
            fn();
        }, (err: any) => {
            if (errorMsg) {
                expect(err.message).toEqual(errorMsg);
            } else {
                expect(err && err.stack || err || undefined).toBeUndefined();
            }
            done();
        });
    };
}

describe('Protractor sync test cases', () => {
    let testArea: ElementFinderSync;

    beforeAll(createTest(() => {
        //Make sure we are starting on a fresh page
        browserSync.get('data:,');

        appendTestArea({
            innerHtml: '<span class="element-does-exist"></span>'
        });

        testArea = elementSync.findElement('#' + TEST_AREA_ID);
    }));

    it('should fail if an element is not supposed to exist but is found #integrationSuite', createTest(() => {
        testArea.assertElementDoesNotExist('.element-does-exist');
    }));

    it('should pass if an element is not supposed to exist and is missing #integrationSuite', createTest(() => {
        testArea.assertElementDoesNotExist('.does-not-exist');
    }));


    it('can retry if they fail when configured #integrationSuite', createTest(() => {
        const retryDir = '/tmp/lambda_protractor/build/test/test/e2e/retry_attempts/';
        const retryFileName = 'someRetry.json';
        const retryInfo = {
            name: 'Protractor sync test cases can retry if they fail when configured #integrationSuite',
            attemptNumber: 1,
            errorMessage: 'HTTP 500'
        };
        const retryJson = JSON.stringify(retryInfo);
        fs.writeFile(path.join(retryDir, retryFileName), retryJson, function (err) {
            if (err) {
                throw err;
            }
        });
    }));

    it('can be skipped if we want them to #integrationSuite');

    it('can be skipped by protractor but filtered from final report (#integrationSuite, #quarantine)');

    /* Test is disabled, but still needs to be on the report in some way.
        it('can be disabled and hidden from the Jasmine reporter #integrationSuite', createTest(() => {
          testArea.assertElementDoesNotExist(by.buttonText('button does not exist'));
        }));
        */
});
