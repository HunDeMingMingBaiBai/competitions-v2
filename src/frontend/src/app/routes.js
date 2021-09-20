/**
 * @description codabench routes
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import React from 'react';
import { Route, Switch } from 'react-router';
import Home from '@/home';
import Public from '@/public';
import Management from '@/management';

const Routes = () => (
  <Switch>
    <Route
      exact
      path='/'
      component={ Home }
    />
    <Route
      path='/competitions'
      component={ Management }
      exact
    />
    <Route
      path='/competitions/public'
      component={ Public }
    />
  </Switch>
);

export default Routes;
