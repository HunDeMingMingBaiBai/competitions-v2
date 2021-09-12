/**
 * @description
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import io from './utils/io';
const HOME = 'home';

io.create(HOME, {
  getCompetitionsFrontpage: {
    method: 'get',
    url: '/api/competitions/front_page',
  },
  getGeneralStatus: {
    method: 'get',
    url: '/api/get_general_status'
  },
  getCompetitions: {
    method: 'get',
    url: '/api/competitions'
  },
  getPublicCompetitions: {
    method: 'get',
    url: '/api/competitions/public',
    transformer: (config) => {
      const { page } = config;
      return {
        params: {
          page
        }
      }
    }
  }
});

export const homeApi = io.getApis(HOME);
