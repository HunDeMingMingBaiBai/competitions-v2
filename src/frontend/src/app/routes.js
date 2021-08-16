/**
 * @file lumos routes
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import React from 'react';
import { Route, Switch } from 'react-router';
import Page from '../page'

const Routes = () => (
  <Switch>
    <Route
      exact
      path='/'
      component={Page}
    />
  </Switch>
);

export default Routes;
