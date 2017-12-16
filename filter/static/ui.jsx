/* globals Infinite, React, ReactDOM, URI, fetch */

(function () {
  // Root of the app, defined in a script tag in HTML
  const APPROOT = window.APPROOT || '';

  const keyValuePairsToMap = arr => Object.assign(...arr.map(([k, v]) => ({[k]: v})));

  const MEMBER_AFFILIATIONS = [
    ['陈观慧', 's2'],
    ['陈思', 's2'],
    ['成珏', 's2'],
    ['戴萌', 's2'],
    ['蒋芸', 's2'],
    ['孔肖吟', 's2'],
    ['李宇琪', 's2'],
    ['吕一', 's2'],
    ['莫寒', 's2'],
    ['潘燕琦', 's2'],
    ['钱蓓婷', 's2'],
    ['邱欣怡', 's2'],
    ['沈之琳', 's2'],
    ['孙芮', 's2'],
    ['温晶婕', 's2'],
    ['吴哲晗', 's2'],
    ['徐晨辰', 's2'],
    ['徐子轩', 's2'],
    ['许佳琪', 's2'],
    ['袁丹妮', 's2'],
    ['袁雨桢', 's2'],
    ['张语格', 's2'],
    ['赵晔', 's2'],

    ['陈佳莹', 'n2'],
    ['陈问言', 'n2'],
    ['冯薪朵', 'n2'],
    ['龚诗淇', 'n2'],
    ['何晓玉', 'n2'],
    ['黄婷婷', 'n2'],
    ['黄彤扬', 'n2'],
    ['江真仪', 'n2'],
    ['金莹玥', 'n2'],
    ['鞠婧祎', 'n2'],
    ['李艺彤', 'n2'],
    ['林思意', 'n2'],
    ['刘菊子', 'n2'],
    ['刘瀛', 'n2'],
    ['陆婷', 'n2'],
    ['马凡', 'n2'],
    ['万丽娜', 'n2'],
    ['许逸', 'n2'],
    ['易嘉爱', 'n2'],
    ['曾艳芬', 'n2'],
    ['张雨鑫', 'n2'],
    ['赵粤', 'n2'],

    ['郭倩芸', 'h2'],
    ['郝婉晴', 'h2'],
    ['姜涵', 'h2'],
    ['李清扬', 'h2'],
    ['林楠', 'h2'],
    ['刘炅然', 'h2'],
    ['刘佩鑫', 'h2'],
    ['沈梦瑶', 'h2'],
    ['孙珍妮', 'h2'],
    ['王柏硕', 'h2'],
    ['王奕', 'h2'],
    ['吴燕文', 'h2'],
    ['谢妮', 'h2'],
    ['熊沁娴', 'h2'],
    ['徐晗', 'h2'],
    ['徐伊人', 'h2'],
    ['许杨玉琢', 'h2'],
    ['杨惠婷', 'h2'],
    ['袁航', 'h2'],
    ['袁一琦', 'h2'],
    ['张昕', 'h2'],

    ['陈琳', 'x'],
    ['冯晓菲', 'x'],
    ['李晶', 'x'],
    ['李钊', 'x'],
    ['林忆宁', 'x'],
    ['祁静', 'x'],
    ['邵雪聪', 'x'],
    ['宋昕冉', 'x'],
    ['孙歆文', 'x'],
    ['孙亚萍', 'x'],
    ['汪佳翎', 'x'],
    ['汪束', 'x'],
    ['王晓佳', 'x'],
    ['谢天依', 'x'],
    ['杨冰怡', 'x'],
    ['杨韫玉', 'x'],
    ['姚祎纯', 'x'],
    ['张丹三', 'x'],
    ['张嘉予', 'x'],

    ['陈韫凌', 'x2'],
    ['费沁源', 'x2'],
    ['洪珮雲', 'x2'],
    ['姜杉', 'x2'],
    ['蒋舒婷', 'x2'],
    ['李佳恩', 'x2'],
    ['林歆源', 'x2'],
    ['刘增艳', 'x2'],
    ['吕梦莹', 'x2'],
    ['潘瑛琪', 'x2'],
    ['宋雨珊', 'x2'],
    ['陶波尔', 'x2'],
    ['许嘉怡', 'x2'],
    ['徐诗琪', 'x2'],
    ['严佼君', 'x2'],
    ['於佳怡', 'x2'],
    ['曾晓雯', 'x2'],
    ['张文静', 'x2'],
    ['张怡', 'x2'],

    // Former members
    ['刘力玮', 'former-s2'],
    ['申月姣', 'former-s2'],
    ['赵韩倩', 'former-s2'],
    ['赵嘉敏', 'former-s2'],

    ['邓艳秋菲', 'former-n2'],
    ['董艳芸', 'former-n2'],
    ['葛佳慧', 'former-n2'],
    ['罗兰', 'former-n2'],
    ['孟玥', 'former-n2'],
    ['钱艺', 'former-n2'],
    ['唐安琪', 'former-n2'],
    ['徐真', 'former-n2'],
    ['张雅梦', 'former-n2'],
    ['周怡', 'former-n2'],

    ['陈怡馨', 'former-h2'],
    ['王金铭', 'former-h2'],
    ['王璐', 'former-h2'],
    ['王露皎', 'former-h2'],
    ['文文', 'former-h2'],
    ['赵梦婷', 'former-h2'],

    ['闫明筠', 'former-x'],
    ['张韵雯', 'former-x'],

    ['陈音', 'former-x2'],
    ['贺苏堃', 'former-x2'],
    ['邹佳佳', 'former-x2']
  ];

  const MEMBER_AFFILIATION_MAP = keyValuePairsToMap(MEMBER_AFFILIATIONS);

  const SEVEN_SENSES_MEMBERS = [
    '戴萌',
    '孔肖吟',
    '许佳琪',
    '张语格',
    '赵粤',
    '许杨玉琢',
    '陈琳'
  ];

  const STAGE_AFFILIATIONS = [
    ['特别公演', ''],
    ['命运的X号', 'x'],
    ['以爱之名', 'n2'],
    ['第48区', 's2'],
    ['我们向前冲', ''],
    ['美丽世界', 'h2'],
    ['代号XⅡ', 'x2'],
    ['梦想的旗帜', 'x'],
    ['专属派对', 'n2'],
    ['心的旅程', 's2']
  ];

  const STAGE_AFFILIATION_MAP = keyValuePairsToMap(STAGE_AFFILIATIONS);

  const TEAM_DISPLAY_NAMES = {
    s2: 'SⅡ',
    n2: 'NⅡ',
    h2: 'HⅡ',
    x: 'X',
    x2: 'XⅡ',
    'former-s2': '前SⅡ',
    'former-n2': '前NⅡ',
    'former-h2': '前HⅡ',
    'former-x': '前X',
    'former-x2': '前XⅡ',
    '7senses': '7SENSES'
  };

  const prefixByTeam = (str, team) => (team in TEAM_DISPLAY_NAMES)
        ? `${TEAM_DISPLAY_NAMES[team]} - ${str}`
        : str;

  const stageBelongsToTeam = (stage, team) => (team === '' || STAGE_AFFILIATION_MAP[stage] === team ||
                                               (team === '7senses' &&
                                                (stage === 'special' || stage === '特别公演')));

  const memberInTeam = (member, team) => (team === '' ||
                                          MEMBER_AFFILIATION_MAP[member] === team ||
                                          MEMBER_AFFILIATION_MAP[member] === `former-${team}` ||
                                          (team === '7senses' && SEVEN_SENSES_MEMBERS.indexOf(member) !== -1));

  const getCurrentFilters = () => {
    const queryParams = URI(window.location).query(true);
    var filters = {};
    for (const key of ['year', 'team', 'stage', 'member']) {
      const vals = queryParams[key];
      if (vals === undefined) {
        filters[key] = '';
      } else if (Array.isArray(vals)) {
        // Multiple values specified, use the last one.
        filters[key] = vals[-1];
      } else {
        filters[key] = vals;
      }
    }
    return filters;
  };

  const Filters = React.createClass({
    getInitialState: function () {
      return getCurrentFilters();
    },

    handleChange (event) {
      const target = event.target;
      const name = target.name;
      const value = target.value;

      var updated = {[name]: value};
      // If the team selection has been updated, make sure to reset the stage
      // and member selections if they no longer belong to the newly selected
      // team.
      if (name === 'team') {
        if (!stageBelongsToTeam(this.state.stage, value)) {
          updated.stage = '';
        }
        if (!memberInTeam(this.state.member, value)) {
          updated.member = '';
        }
      }
      this.setState(updated);
    },

    handleSubmit (event) {
      const qs = ['year', 'team', 'stage', 'member']
            .filter((key) => this.state[key] !== '')
            .map((key) => `${key}=${encodeURIComponent(this.state[key])}`)
            .join('&');
      window.location = qs ? `${APPROOT}/?${qs}` : `${APPROOT}/`;
      event.preventDefault();
    },

    render: function () {
      const thisYear = new Date().getFullYear();
      const yearOptions = [
        <option value='' key=''>无限制</option>
      ];
      for (var year = 2016; year <= thisYear; year++) {
        yearOptions.push(
          <option value={year}>{year}</option>
        );
      }
      const selectedYear = this.state.year;

      const teamOptions = [
        <option value='' key=''>无限制</option>
      ].concat(
        ['s2', 'n2', 'h2', 'x', 'x2', '7senses'].map((team) => (
          <option value={team} key={team}>{TEAM_DISPLAY_NAMES[team]}</option>
        ))
      );
      const selectedTeam = this.state.team;

      const stageOptions = [
        <option value='' key=''>无限制</option>
      ].concat(
        STAGE_AFFILIATIONS
          .filter(([stage, _]) => stageBelongsToTeam(stage, selectedTeam))
          .map(([stage, team]) => {
            // Internal name of the stage, used by the API.
            const stageInternal = (stage === '特别公演') ? 'special' : stage;
            return <option value={stageInternal} key={stage}>{prefixByTeam(stage, team)}</option>;
          })
      );

      const memberOptions = [
        <option value='' key=''>无限制</option>
      ]
      var optgroup = []
      var optgroupTeam = null
      MEMBER_AFFILIATIONS
        .filter(([member, _]) => memberInTeam(member, selectedTeam))
        .forEach(([member, team]) => {
          if (team !== optgroupTeam) {
            if (optgroup.length > 0) {
              memberOptions.push(
                <optgroup label={TEAM_DISPLAY_NAMES[optgroupTeam]}>{optgroup}</optgroup>
              );
            }
            optgroup = [];
            optgroupTeam = team;
          }
          optgroup.push(
            <option value={member} key={member}>{prefixByTeam(member, team)}</option>
          );
        });
      if (optgroup.length > 0) {
        memberOptions.push(
          <optgroup label={TEAM_DISPLAY_NAMES[optgroupTeam]}>{optgroup}</optgroup>
        );
      }

      return (
        <form onSubmit={this.handleSubmit}>
          <span className='filter'>
            <label>年份</label>
            <select name='year' value={this.state.year} onChange={this.handleChange}>
              {yearOptions}
            </select>
          </span>
          <span className='filter'>
            <label>队伍</label>
            <select name='team' value={this.state.team} onChange={this.handleChange}>
              {teamOptions}
            </select>
          </span>
          <span className='filter'>
            <label>公演</label>
            <select name='stage' value={this.state.stage} onChange={this.handleChange}>
              {stageOptions}
            </select>
          </span>
          <span className='filter'>
            <label>成员</label>
            <select name='member' value={this.state.member} onChange={this.handleChange}>
              {memberOptions}
            </select>
          </span>
          <input type='submit' value='筛选' />
        </form>
      );
    }
  });

  const PerformanceEntry = React.createClass({
    render: function () {
      const entry = this.props.entry;
      const imgsrc = (entry.video_id !== null)
            ? `https://i.ytimg.com/vi/${entry.video_id}/mqdefault.jpg`
            : `${APPROOT}/static/unavailable.jpg`;
      const youtubeLink = (entry.video_id !== null)
            ? `https://youtu.be/${entry.video_id}`
            : null;
      const titleAbridged = entry.title.replace(/(\d{8}) SNH48 /, '$1 ');
      var slug;
      if (entry.video_id) {
        slug = entry.video_id;
      } else if (entry.snh48club_video_id) {
        slug = `club:${entry.snh48club_video_id}`;
      }

      var imgElem = <img className='thumbnail' src={imgsrc} alt={titleAbridged} />;
      if (youtubeLink) {
        imgElem = <a href={youtubeLink} target='_blank'>{imgElem}</a>;
      }

      const titleElem = slug
            ? <span className='title'><a href={`performance/${encodeURIComponent(slug)}`}>{titleAbridged}</a></span>
            : <span className='title'>{titleAbridged}</span>;

      var performers = [];
      entry.performers.split(',').slice(0, -1).forEach((performer, index) => {
        if (index > 0) {
          // Space-separate names
          performers.push(' ');
        }
        const link = URI.build({
          path: `${APPROOT}/`,
          query: URI.buildQuery({member: performer})
        });
        performers.push(<a key={performer} href={link}>{performer}</a>);
      });
      const performersElem = <span className='performers'>{performers}</span>;

      return <div className='entry'>{imgElem}{titleElem}{performersElem}</div>;
    }
  });

  const PerformanceList = React.createClass({
    filters: getCurrentFilters(),
    resultsPerPage: 50,

    getInitialState: function () {
      return {
        elements: [],
        total: undefined,
        page: 0,
        isInfiniteLoading: false,
        errored: false
      };
    },

    buildElements: function (callback) {
      if (this.state.total !== undefined &&
          this.state.total <= this.resultsPerPage * this.state.page) {
        // Already exhausted all entries
        callback([]);
        return;
      }

      this.state.page++;
      var queryParams = {
        page: this.state.page,
        results_per_page: this.resultsPerPage
      };
      for (const key of ['year', 'team', 'stage', 'member']) {
        if (this.filters[key] !== '') {
          queryParams[key] = this.filters[key];
        }
      }
      const apiUrl = URI.build({
        path: `${APPROOT}/api/performance`,
        query: URI.buildQuery(queryParams)
      });
      fetch(apiUrl)
        .then((response) => {
          if (response.status !== 200) {
            this.state.errored = true;
            return {objects: []};
          }
          return response.json();
        })
        .then((data) => {
          if (this.state.total === undefined) {
            this.state.total = data.num_results;
          }
          const elements = data.objects.map((entry) => {
            var key;
            if (entry.video_id) {
              key = entry.video_id;
            } else if (entry.snh48club_video_id) {
              key = `club:${entry.snh48club_video_id}`;
            } else {
              key = entry.title;
            }
            return <PerformanceEntry key={key} entry={entry} />;
          });
          callback(elements);
        });
    },

    handleInfiniteLoad: function () {
      this.setState({
        isInfiniteLoading: true
      });
      this.buildElements((elements) => {
        this.setState({
          isInfiniteLoading: false,
          elements: this.state.elements.concat(elements)
        });
      });
    },

    elementInfiniteLoad: function () {
      return <div className='loading'>加载中...</div>;
    },

    render: function () {
      const countElem = (this.state.total !== undefined)
            ? <div className='count'>共{this.state.total}场</div>
            : <div className='count' />;
      const errorElem = this.state.errored
            ? <div className='error'>获取数据失败。请刷新重试。</div>
            : null;
      return (
        <div>
          {countElem}
          <Infinite elementHeight={110}
            infiniteLoadBeginEdgeOffset={550}
            onInfiniteLoad={this.handleInfiniteLoad}
            loadingSpinnerDelegate={this.elementInfiniteLoad()}
            isInfiniteLoading={this.state.isInfiniteLoading}
            useWindowAsScrollContainer
          >
            {this.state.elements}
          </Infinite>
          {errorElem}
        </div>
      );
    }
  });

  ReactDOM.render(<Filters />, document.getElementById('filters'));
  ReactDOM.render(<PerformanceList />, document.getElementById('results'));
})();
