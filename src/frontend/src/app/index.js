/**
 * @description App Entry
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import React, { PureComponent } from 'react';
import { HashRouter } from 'react-router-dom';
import { createBrowserHistory } from 'history';
import Routes from './routes';


const history = createBrowserHistory();

class App extends PureComponent {
  render() {
    return (
      <HashRouter hashHistory={ history }>
        <div className='base-layout'>
          <Routes />
        </div>
      </HashRouter>
    );
  }
}

export default App;
