/**
 * @description Codalab Search Component
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import React, { useState } from 'react';
import { Search } from 'semantic-ui-react';
import { homeApi } from '@/common/api';
import './index.less';

const CodalabSearch = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  // const [value, setValue] = useState(null);

  // const resultRenderer = () => <Competition />

  const handleResultSelect = () => { }

  const handleSearchChange = async (e, { value }) => {
    setLoading(true);
    try {
      const { data } = await homeApi.competitions({ params: { search: value } });
      setResults(data);
    } catch (err) {
      console.log(err);
    }
    setLoading(false);
  }

  return (
    <Search
      loading={ loading }
      results={ results }
      input={ { placeholder: "Search competitions", className: 'search-width' } }
      onResultSelect={ handleResultSelect }
      onSearchChange={ handleSearchChange }
    />
  )
}
export default CodalabSearch;
