/**
 * @description Codalab Page Common Wrap
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import React, { useEffect, useState } from 'react';
import { Dropdown, Icon } from 'semantic-ui-react';
import { useHistory, useLocation } from 'react-router-dom';
import CodalabSearch from '@/common/components/CodalabSearch';

const CodalabWrap = (props) => {
  const [showLogo, setShowLogo] = useState(false);
  const history = useHistory();
  const location = useLocation();

  useEffect(() => {
    if (location.pathname) {
      setShowLogo(true);
    } else {
      setShowLogo(false);
    }
  }, [location])

  const handleManagementClicked = () => {
    history.push({
      pathname: '/competitions',
    });
  };
  const handlePublicClicked = () => {
    history.push({
      pathname: '/competitions/public',
    });
  };
  const handleMenuDropdownClick = (e, data) => {
    const { name } = data;
    if (name === 'management') {
      handleManagementClicked();
    } else if (name === 'public') {
      handlePublicClicked();
    }
  };

  return (
    <div className="pusher">
      <div id="header" className="ui inverted vertical center aligned segment masthead jumbotron">
        <div id="bg"></div>
        <div className="ui container">
          <div id="topleft_menu" className="ui secondary inverted menu">
            <span className="left item">
              <a href="/" id="home-logo">
                <img className="ui mini image" src="/common/image/Cha_Logo.png" />
              </a>
              <CodalabSearch />
            </span>
            <div className="right menu item">
              <Dropdown
                className="item"
                trigger={ (<span><Icon name="trophy" />Benchmarks</span>) }
              >
                <Dropdown.Menu>
                  <Dropdown.Item name="management" onClick={ handleMenuDropdownClick }>Management</Dropdown.Item>
                  <Dropdown.Item name="public" onClick={ handleMenuDropdownClick }>Public</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>

              <a className="item" href="">
                <i selenium="tasks" className="ui small file icon"></i>
                Resources
              </a>
              <a className="item" href="">
                <i className="ui small computer icon"></i>
                Queue Management
              </a>
              <div id="user_dropdown" className="ui dropdown item">
                <div className="text">
                  <i className="icon user outline"></i>
                </div>
                <i className="dropdown icon"></i>
                <div className="menu">
                  <div className="ui divider"></div>
                  <div className="header">Account</div>
                  <a className="item" href="">
                    <i className="icon user"></i>
                    View Profile
                  </a>
                  <a className="item" href="">
                    <i className="edit icon"></i>
                    Edit profile
                  </a>
                  <a className="item" href="{% url 'profiles:user_notifications' username=user.username %}">
                    <i className="bell icon"></i>
                    Notifications
                  </a>
                  <a className="item" href="">
                    <i className="icon sign out"></i>
                    Logout
                  </a>
                  <div className="ui divider"></div>
                  <div className="header">Organizations</div>
                  <a className="item" href="">
                    <i className="plus icon"></i>
                    Create Organization
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
        { showLogo && (
          <div className="ui text container">
            <img id="jumbo_logo" src="/common/image/codabench.png" />
            <div className="subtitle"><h1> BETA </h1></div>
          </div>
        ) }
      </div>

      <div id="page_content" className="ui container grid">
        <div className="row">
          { props.children }
        </div>
      </div>

      <div className="ui inverted vertical footer segment">
        <div className="ui container">
          <div className="ui stackable inverted equal height stackable grid">
            <div className="three wide column">
              <h4 className="ui inverted header">Chasuite</h4>
              <div className="ui inverted link list">
                <a href="https://competitions.codalab.org/" className="item">Competitions v1.5</a>
                <a href="http://chahub.org/" className="item">Chahub</a>
                <a href="https://chagrade.lri.fr/" className="item">Chagrade</a>
              </div>
            </div>
            <div className="three wide column">
              <h4 className="ui inverted header">About</h4>
              <div className="ui inverted link list">
                <a href="https://github.com/codalab/codalab-competitions/wiki/Project_About_CodaLab" className="item">About</a>
                <a href="https://github.com/codalab/competitions-v2" className="item">Github</a>
                <a href="https://github.com/codalab/codalab-competitions/wiki/Privacy" className="item">Privacy and Terms</a>
                <a href="" className="item">API Docs</a>
              </div>
            </div>
            <div className="three wide column"></div>
            <div className="seven wide column">
              <h4 className="ui inverted header">Codalab v2</h4>
              <p>Join us on <a href="https://github.com/codalab/competitions-v2" target="_blank">Github</a> for contact &amp; bug reports</p>
              <p>Questions about the platform? See our <a href="https://github.com/codalab/competitions-v2/wiki" target="_blank">Wiki</a> for more information.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

  )
}
export default CodalabWrap;
