# API docs

## Performances

Get list of performances, subject to various filters.

```http
GET https://snh48live.org/filter/api/performance
```

### Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| `team`    | No       | Filtering criterion. Team identifier: `s2`, `n2`, `h2`, `x`, `x2`, `7senses` or `joint` (for joint stages). |
| `stage`   | No       | Filtering criterion. Stage name: `special` (for special stages), `心的旅程`, `专属派对`, `梦想的旗帜`, `代号XⅡ`, `美丽世界`, `我们向前冲`, or the name of any stage newer than the above. |
| `member`  | No       | Filtering criterion. Member name: e.g. `莫寒`. |
| `page`    | No       | Page number. Default is 1. |
| `results_per_page` | No | Number of results per page; should not exceed 100. Default is 10. |

Any combination (zero or more) of the filtering criteria `team`, `stage` and `member` is allowed.

### Response

The response of a successful request contains pagination info and a list of metadata objects in `.objects`. Entries are sorted in reverse chronological order. Each metadata object has the following keys:

| Key | Description |
| --- | ----------- |
| `id` | A numerial internal ID; should be stable, but do not rely on that. |
| `performers` | A comma-delimited list of performer names for the specific performance. The string ends in a comma. |
| `snh48club_video_id` | ID of the performance on snh48club.com. The performance should be located at `http://www.snh48club.com/video/{snh48club_video_id}.html`, from which the list of performers was compiled. |
| `special` | Boolean indicating whether the performance was a special stage. Somewhat opinionated. |
| `stage` | Title of the stage, if any, e.g., `心的旅程`. |
| `team` | Identifier of the performing team. Refer to the `team` query parameter. |
| `title` | Title of the specific performance. |
| `video_id` | YouTube video ID, if the performance has been uploaded to the SNH48 Live channel. |

### Sample request

```http
GET https://snh48live.org/filter/api/performance?member=莫寒&results_per_page=3

{
  "num_results": 46,
  "objects": [
    {
      "id": 146,
      "performers": "陈观慧,陈思,蒋芸,吕一,李宇琪,莫寒,潘燕琦,钱蓓婷,孙芮,沈之琳,吴哲晗,徐晨辰,徐子轩,袁雨桢,赵韩倩,赵晔,",
      "snh48club_video_id": "19258",
      "special": false,
      "stage": "心的旅程",
      "team": "s2",
      "title": "20170420 SNH48 Team SⅡ 心的旅程 53",
      "video_id": "ygm4WaeO6cQ"
    },
    {
      "id": 143,
      "performers": "陈观慧,成珏,戴萌,蒋芸,孔肖吟,吕一,莫寒,钱蓓婷,孙芮,沈之琳,徐晨辰,许佳琪,徐子轩,袁丹妮,袁雨桢,赵韩倩,冯晓菲,",
      "snh48club_video_id": "19116",
      "special": false,
      "stage": "心的旅程",
      "team": "s2",
      "title": "20170416 SNH48 Team SⅡ 心的旅程 52 戴萌生日主题公演",
      "video_id": "jd74BATSAOo"
    },
    {
      "id": 141,
      "performers": "成珏,戴萌,蒋芸,孔肖吟,吕一,莫寒,钱蓓婷,孙芮,沈之琳,徐晨辰,许佳琪,徐子轩,袁丹妮,袁雨桢,赵韩倩,冯晓菲,",
      "snh48club_video_id": "19058",
      "special": false,
      "stage": "心的旅程",
      "team": "s2",
      "title": "20170415 SNH48 Team SⅡ 心的旅程 51",
      "video_id": "SOcOjHCQaAw"
    }
  ],
  "page": 1,
  "total_pages": 16
}
```
