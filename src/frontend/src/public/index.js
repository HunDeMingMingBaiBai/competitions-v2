/**
 * @description Benchmarks: Public Competitions List
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import React, { useEffect, useMemo, useState } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import qs from 'qs';
import { homeApi } from '@/common/api';
import CodalabWrap from '@/common/components/CodalabWrap';
import Competition from '@/home/components/Competition';

import './index.less';

const Public = () => {
  const defaultParams = {
    page: 1,
    page_size: 2
  }
  const [competitions, setCompetitions] = useState([]);
  const [count, setCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(defaultParams.page);
  const [pageSize, setPageSize] = useState(defaultParams.page_size);
  const history = useHistory();
  const location = useLocation();

  useEffect(() => {
    reload();
  }, [location]);

  const getFilters = () => {
    const { search } = location;
    return {
      ...defaultParams,
      ...qs.parse(search.split('?')[1])
    }
  };

  const fetchList = async (params) => {
    try {
      const { data } = await homeApi.getPublicCompetitions({ ...params });
      setCompetitions(data.results);
      setCount(data.count);
    } catch (err) {
      console.log(err);
    }
  }

  const reload = () => {
    const params = getFilters();
    const { page, page_size } = params;
    history.push({
      pathname: location.pathname,
      search: qs.stringify(params)
    });
    // synchronise states
    setCurrentPage(+page);
    setPageSize(+page_size);

    fetchList(params);
  };

  const isBackDisabled = useMemo(() => {
    return currentPage <= 1;
  }, [currentPage]);
  const isNextDisabled = useMemo(() => {
    return currentPage > count / pageSize;
  }, [currentPage, count]);

  const changePage = (page) => {
    const params = getFilters();
    history.push({
      pathname: location.pathname,
      search: qs.stringify(params)
    });
    setCurrentPage(page);
  }

  const handleBackClicked = () => {
    if (!isBackDisabled) {
      const nextPage = currentPage - 1;
      changePage(nextPage);
    }
  };
  const handleNextClicked = () => {
    if (!isNextDisabled) {
      const nextPage = currentPage + 1;
      changePage(nextPage);
    }
  };

  return (
    <div id="public-list">
      <h1>Public Competitions</h1>
      <div className={ `pagination-nav ` }>
        <button onClick={ handleBackClicked } className={ `float-left ui inline button active ${isBackDisabled ? 'disabled' : ''}` }>Back</button>
        { currentPage } of { Math.ceil(count / pageSize) }
        <button onClick={ handleNextClicked } className={ `float-right ui inline button active ${isNextDisabled ? 'disabled' : ''}` }>Next</button>
      </div>
      { competitions.map((item) => (<Competition data={ item } />)) }
    </div>
  )
};
export default Public;
