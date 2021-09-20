/**
 * @description App Entry
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import React, { PureComponent } from 'react';
import { HashRouter } from 'react-router-dom';
import { createBrowserHistory } from 'history';
import CodalabWrap from '@/common/components/CodalabWrap';
import Routes from './routes';

import './index.less';


const history = createBrowserHistory();

class App extends PureComponent {
  render() {
    return (
      <HashRouter hashHistory={ history }>
        <div className='base-layout'>
          <CodalabWrap>
            <Routes />
          </CodalabWrap>
        </div>
      </HashRouter>
    );
  }
}

export default App;
