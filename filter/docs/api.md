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
| `live_id` | ID of the performance on live.snh48.com. The VOD should be located at `http://live.snh48.com/Index/invedio/id/{live_id}`. |
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
  "num_results": 49,
  "objects": [
    {
      "id": 183,
      "live_id": "213",
      "performers": "陈思,戴萌,蒋芸,孔肖吟,李宇琪,吕一,莫寒,潘燕琦,钱蓓婷,孙芮,吴哲晗,徐晨辰,徐子轩,许佳琪,袁丹妮,袁雨桢,赵韩倩,冯晓菲,",
      "snh48club_video_id": "20580",
      "special": false,
      "stage": "心的旅程",
      "team": "s2",
      "title": "20170527 SNH48 Team SⅡ 心的旅程 59",
      "video_id": "Ujcn-zxRuUE"
    },
    {
      "id": 181,
      "live_id": null,
      "performers": "陈思,戴萌,蒋芸,吕一,莫寒,潘燕琦,钱蓓婷,孙芮,吴哲晗,徐晨辰,徐子轩,许佳琪,袁丹妮,袁雨桢,赵韩倩,冯晓菲,",
      "snh48club_video_id": "20578",
      "special": false,
      "stage": "心的旅程",
      "team": "s2",
      "title": "20170525 SNH48 Team SⅡ 心的旅程 58",
      "video_id": "QEpMyr-NQhk"
    },
    {
      "id": 179,
      "live_id": "210",
      "performers": "陈观慧,陈思,戴萌,蒋芸,孔肖吟,吕一,莫寒,潘燕琦,钱蓓婷,孙芮,吴哲晗,徐晨辰,许佳琪,徐子轩,袁丹妮,赵韩倩,冯晓菲,",
      "snh48club_video_id": "20468",
      "special": false,
      "stage": "心的旅程",
      "team": "s2",
      "title": "20170521 SNH48 Team SⅡ 心的旅程 57 孔肖吟生日主题公演",
      "video_id": "G6M_hiOCV-4"
    }
  ],
  "page": 1,
  "total_pages": 17
}
```
