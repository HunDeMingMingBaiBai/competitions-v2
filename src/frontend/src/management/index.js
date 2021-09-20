/**
 * @description Benchmarks: Management
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import React, { useEffect, useState } from 'react';
import { Table } from 'semantic-ui-react'
import { timeSince } from '@/common/utils/helper';
import { homeApi } from '@/common/api';

const Management = () => {
  const [runningList, setRunningList] = useState([]);
  const [competitionList, setCompetitionList] = useState([]);
  useEffect(() => {
    reload();
  }, [])

  const reload = async () => {
    try {
      const { data: runningList } = await homeApi.getCompetitions({ params: { mine: true, type: 'any' } });
      setRunningList(runningList);
      const { data: competitions } = await homeApi.getCompetitions({ params: { participating_in: true } });
      setCompetitionList(competitions);
    } catch (err) {
      console.log(err)
    }
  }

  const renderRunningTable = () => {
    return (
      <Table className="ui celled compact table participation">
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell singleLine>Name</Table.HeaderCell>
            <Table.HeaderCell>Type</Table.HeaderCell>
            <Table.HeaderCell>Uploaded...</Table.HeaderCell>
            <Table.HeaderCell>Publish</Table.HeaderCell>
            <Table.HeaderCell>Edit</Table.HeaderCell>
            <Table.HeaderCell>Delete</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          { runningList.map(competition => (
            <Table.Row>
              <Table.Cell><a href="{ URLS.COMPETITION_DETAIL(competition.id) }">{ competition.title }</a></Table.Cell>
              <Table.Cell className="center aligned">{ competition.competition_type }</Table.Cell>
              <Table.Cell>{ timeSince(Date.parse(competition.created_when)) } ago</Table.Cell>
              <Table.Cell className="center aligned">
                <button className="mini ui button published icon { grey: !competition.published, green: competition.published }"
                  onclick="{ toggle_competition_publish.bind(this, competition) }">
                  <i className="icon file"></i>
                </button>
              </Table.Cell>
              <Table.Cell className="center aligned">
                <a href="{ URLS.COMPETITION_EDIT(competition.id) }"
                  className="mini ui button blue icon">
                  <i className="icon edit"></i>
                </a>
              </Table.Cell>
              <Table.Cell className="center aligned">
                <button className="mini ui button red icon"
                  onclick="{ delete_competition.bind(this, competition) }">
                  <i className="icon delete"></i>
                </button>
              </Table.Cell>
            </Table.Row>
          )) }
          {/* { competitions.map(competition => renderCompetition(competition)) } */ }
        </Table.Body>
      </Table>
    )
  }
  const renderCompetitionListTable = () => {
    return (
      <Table className="ui celled compact table">
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell singleLine>Name</Table.HeaderCell>
            <Table.HeaderCell>Uploaded...</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          { competitionList.map(competition => (
            <Table.Row style="height: 42px;">
              <Table.Cell><a href="{ URLS.COMPETITION_DETAIL(competition.id) }">{ competition.title }</a></Table.Cell>
              <Table.Cell>{ timeSince(Date.parse(competition.created_when)) } ago</Table.Cell>
            </Table.Row>
          )) }
        </Table.Body>
      </Table>
    )
  }

  return (
    <div>
      <div className="ui center aligned grid">
        <div className="fourteen wide column">
          <h1 style={ { float: 'left', display: 'inline-block' } }>Benchmark Management</h1>
          <a className="ui right floated green button" href="{ URLS.COMPETITION_UPLOAD }">
            <i className="upload icon"></i> Upload
          </a>
          <a className="ui right floated green button" href="{ URLS.COMPETITION_ADD }">
            <i className="add square icon"></i> Create
          </a>
        </div>
      </div>
      <div className="ui vertical stripe segment">
        <div className="ui middle aligned stackable grid container centered">
          <div className="row">
            <div className="fourteen wide column">
              <div className="ui fluid secondary pointing tabular menu">
                <a className="active item" data-tab="running">Benchmarks I'm Running</a>
                <a className="item" data-tab="participating">Benchmarks I'm In</a>
                <div className="right menu">
                  <div className="item">
                    <help_button href="https://github.com/codalab/competitions-v2/wiki/Competition-Management-&-List"></help_button>
                  </div>
                </div>
              </div>
              <div className="ui active tab" data-tab="running">
                { renderRunningTable() }
              </div>
              <div className="ui tab" data-tab="participating">
                { renderCompetitionListTable() }
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
};
export default Management;
