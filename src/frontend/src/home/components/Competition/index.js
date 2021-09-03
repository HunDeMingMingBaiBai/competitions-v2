/**
 * @description Competition Component
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import React from 'react';
import dayjs from 'dayjs'
import './index.less';

const Competition = (props) => {
  const { title, description, created_by, created_when, participant_count } = props.data || {};

  const pretty_description = function (description) {
    return description.substring(0, 90) + (description.length > 90 ? '...' : '') || ''
  }
  const pretty_date = function (date_string) {
    if (!!date_string) {
      // TODO: date intl
      return dayjs(date_string).locale('zh-cn').format('YYYY-MM-DD')
    } else {
      return ''
    }
  }
  return (
    <div className="link-no-deco" href="">
      <div className="tile-wrapper">
        <div className="ui square tiny bordered image img-wrapper">
          <img src="{logo}" />
        </div>
        <div className="comp-info">
          <h4 className="heading">
            { title }
          </h4>
          <p className="comp-description">
            { pretty_description(description) }
          </p>
          <p className="organizer">
            <em>Organized by: <strong>{ created_by }</strong></em>
          </p>
        </div>
        <div className="comp-stats">
          { pretty_date(created_when) }
          <div className="ui divider"></div>
          <strong>{ participant_count }</strong> Participants
        </div>
      </div>
    </div>
  )
}

export default Competition;
