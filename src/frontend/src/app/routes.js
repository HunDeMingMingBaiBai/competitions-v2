/**
 * @description codabench routes
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import React from 'react';
import { Route, Switch } from 'react-router';
import Home from '@/home';

const Routes = () => (
  <Switch>
    <Route
      exact
      path='/'
      component={ Home }
    />
  </Switch>
);

export default Routes;
