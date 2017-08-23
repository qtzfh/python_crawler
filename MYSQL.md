## 项目下mysql表字段以及信息
```
	CREATE TABLE `zhihu_question` (
	  `id` varchar(64) NOT NULL COMMENT '知乎question_id',
	  `title` varchar(64) DEFAULT NULL COMMENT '知乎问题标题',
	  `href` varchar(128) DEFAULT NULL COMMENT '知乎问题url',
	  `create_time` datetime DEFAULT NULL,
	  `update_time` datetime DEFAULT NULL,
	  `execute_type` int(1) DEFAULT '1' COMMENT '1：代表初始状态 2：question_info 添加完毕 3：answer 添加完毕',
	  `is_delete` int(1) DEFAULT '1' COMMENT '是否被关闭',
	  PRIMARY KEY (`id`),
	  UNIQUE KEY `href不能重复` (`href`) USING HASH
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;

	CREATE TABLE `zhihu_answer_info` (
	  `id` varchar(32) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '知乎answer_id',
	  `question_id` varchar(64) CHARACTER SET utf8 DEFAULT NULL,
	  `agree_num` int(11) DEFAULT NULL COMMENT '赞同数',
	  `comment_num` int(11) DEFAULT NULL COMMENT '评论数',
	  `create_time` datetime DEFAULT NULL,
	  `update_time` datetime DEFAULT NULL,
	  `is_delete` int(1) DEFAULT '1',
	  `created_time` varchar(32) CHARACTER SET utf8 DEFAULT NULL COMMENT '知乎创建日期',
	  `url_token` varchar(64) CHARACTER SET utf8 DEFAULT NULL COMMENT '用户主页url',
	  `author_name` varchar(32) CHARACTER SET utf8 DEFAULT NULL COMMENT '用户名称',
	  `content` longtext CHARACTER SET utf8 COMMENT '回答内容',
	  PRIMARY KEY (`id`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

	CREATE TABLE `zhihu_question_info` (
	  `question_id` varchar(64) NOT NULL,
	  `follow_num` int(11) DEFAULT NULL COMMENT '关注人数',
	  `read_num` int(11) DEFAULT NULL COMMENT '浏览次数',
	  `answer_num` int(11) DEFAULT NULL COMMENT '回答次数',
	  `create_time` datetime DEFAULT NULL,
	  `update_time` datetime DEFAULT NULL,
	  `task_day` varchar(32) NOT NULL,
	  `is_delete` int(1) DEFAULT '1' COMMENT '知乎问题每日信息记录',
	  PRIMARY KEY (`question_id`,`task_day`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;


```