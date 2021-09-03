/**
 * @file History Utils 
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import { createBrowserHistory } from 'history';

const history = createBrowserHistory();

export const { push, replace, go, goBack, goForward } = history;
export default history;