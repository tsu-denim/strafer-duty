import * as path from 'path';

export let implicitWaitMs = 5000;
export let retryIntervalMs = 10;
export let clickRetryIntervalMs = 200;

export let autoReselectStaleElements = true;
export let autoRetryClick = true;
export let jQueryLocation = path.join(__dirname, '../../../node_modules/jquery/dist/jquery.js');

export function configure(args: {
  implicitWaitMs?: number,
  retryIntervalMs?: number,
  clickRetryIntervalMs?: number,
  autoReselectStaleElements?: boolean,
  autoRetryClick?: boolean,
  jQueryLocation?: string
}) {
  implicitWaitMs = args.implicitWaitMs || implicitWaitMs;
  retryIntervalMs = args.retryIntervalMs || retryIntervalMs;
  clickRetryIntervalMs = args.clickRetryIntervalMs || clickRetryIntervalMs;

  autoReselectStaleElements = args.autoReselectStaleElements != null ? args.autoReselectStaleElements : autoReselectStaleElements;
  autoRetryClick = args.autoRetryClick != null ? args.autoRetryClick : autoRetryClick;

  jQueryLocation = args.jQueryLocation || jQueryLocation;
}
