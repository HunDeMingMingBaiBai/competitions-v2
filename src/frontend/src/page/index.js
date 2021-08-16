import React, { PureComponent } from 'react';
import { withRouter } from 'react-router';
// import PropTypes from 'prop-types';
import './index.less';

class Page extends PureComponent {
  constructor() {
    super();
    this.state = {
    };
  }

  render() {
    return (
      <div className=''>
        Welcome
      </div>
    );
  }
}
export default withRouter(Page);
