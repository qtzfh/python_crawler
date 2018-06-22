## 项目下mysql表字段以及信息
```
    CREATE TABLE `cookies` (
      `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
      `cookies` varchar(1024) DEFAULT NULL,
      `type` varchar(32) DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

	CREATE TABLE `zhihu_question` (
	  `id` varchar(64) NOT NULL COMMENT '知乎question_id',
	  `title` varchar(64) DEFAULT NULL COMMENT '知乎问题标题',
	  `href` varchar(128) DEFAULT NULL COMMENT '知乎问题url',
	  `create_time` datetime DEFAULT NULL,
	  `update_time` datetime DEFAULT NULL,
	  `execute_type` int(1) DEFAULT '1' COMMENT '1：代表初始状态 2：question_info 添加完毕',
	  `is_delete` int(1) DEFAULT '1' COMMENT '是否被关闭',
	  PRIMARY KEY (`id`),
	  UNIQUE KEY `href不能重复` (`href`) USING HASH
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;

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

    CREATE TABLE `zhihu_special` (
      `special_id` int(11) NOT NULL COMMENT '专栏id',
      `title` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '标题',
      `create_time` datetime NOT NULL COMMENT '创建时间',
      `update_time` datetime NOT NULL COMMENT '修改时间',
      `is_delete` tinyint(1) NOT NULL DEFAULT '1' COMMENT '0：删除 1：未删除',
      PRIMARY KEY (`special_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

	CREATE TABLE `zhihu_topic` (
      `topic_id` int(11) NOT NULL,
      `topic_name` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '话题名',
      `follow_num` int(11) DEFAULT NULL COMMENT '关注数',
      `question_num` int(11) DEFAULT NULL COMMENT '问题数',
      `create_time` datetime NOT NULL,
      `update_time` datetime NOT NULL,
      `is_delete` tinyint(11) unsigned NOT NULL DEFAULT '1' COMMENT '0：删除 1：未删除',
      PRIMARY KEY (`topic_id`),
      KEY `zhihu_topic_name` (`topic_name`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='知乎话题';

    CREATE TABLE `zhihu_topic_question_relation` (
      `topic_id` int(10) unsigned NOT NULL,
      `question_id` int(10) unsigned NOT NULL,
      `create_time` datetime NOT NULL COMMENT '创建时间',
      `update_time` datetime NOT NULL COMMENT '修改时间',
      `is_delete` tinyint(1) unsigned NOT NULL DEFAULT '1' COMMENT '0：删除 1：未删除',
      PRIMARY KEY (`topic_id`,`question_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

    CREATE TABLE `zhihu_topic_special_relation` (
      `topic_id` int(11) NOT NULL COMMENT '问题id',
      `special_id` int(11) NOT NULL COMMENT '专栏id',
      `create_time` datetime NOT NULL COMMENT '创建时间',
      `update_time` datetime NOT NULL COMMENT '修改时间',
      `is_delete` tinyint(4) NOT NULL DEFAULT '1' COMMENT '0：删除 1：未删除',
      PRIMARY KEY (`topic_id`,`special_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;



```
