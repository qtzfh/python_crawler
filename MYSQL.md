## ��Ŀ��mysql���ֶ��Լ���Ϣ
```
	CREATE TABLE `zhihu_question` (
	  `id` varchar(64) NOT NULL COMMENT '֪��question_id',
	  `title` varchar(64) DEFAULT NULL COMMENT '֪���������',
	  `href` varchar(128) DEFAULT NULL COMMENT '֪������url',
	  `create_time` datetime DEFAULT NULL,
	  `update_time` datetime DEFAULT NULL,
	  `execute_type` int(1) DEFAULT '1' COMMENT '1�������ʼ״̬ 2��question_info ������ 3��answer ������',
	  `is_delete` int(1) DEFAULT '1' COMMENT '�Ƿ񱻹ر�',
	  PRIMARY KEY (`id`),
	  UNIQUE KEY `href�����ظ�` (`href`) USING HASH
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;

	CREATE TABLE `zhihu_answer_info` (
	  `id` varchar(32) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '֪��answer_id',
	  `question_id` varchar(64) CHARACTER SET utf8 DEFAULT NULL,
	  `agree_num` int(11) DEFAULT NULL COMMENT '��ͬ��',
	  `comment_num` int(11) DEFAULT NULL COMMENT '������',
	  `create_time` datetime DEFAULT NULL,
	  `update_time` datetime DEFAULT NULL,
	  `is_delete` int(1) DEFAULT '1',
	  `created_time` varchar(32) CHARACTER SET utf8 DEFAULT NULL COMMENT '֪����������',
	  `url_token` varchar(64) CHARACTER SET utf8 DEFAULT NULL COMMENT '�û���ҳurl',
	  `author_name` varchar(32) CHARACTER SET utf8 DEFAULT NULL COMMENT '�û�����',
	  `content` longtext CHARACTER SET utf8 COMMENT '�ش�����',
	  PRIMARY KEY (`id`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

	CREATE TABLE `zhihu_question_info` (
	  `question_id` varchar(64) NOT NULL,
	  `follow_num` int(11) DEFAULT NULL COMMENT '��ע����',
	  `read_num` int(11) DEFAULT NULL COMMENT '�������',
	  `answer_num` int(11) DEFAULT NULL COMMENT '�ش����',
	  `create_time` datetime DEFAULT NULL,
	  `update_time` datetime DEFAULT NULL,
	  `task_day` varchar(32) NOT NULL,
	  `is_delete` int(1) DEFAULT '1' COMMENT '֪������ÿ����Ϣ��¼',
	  PRIMARY KEY (`question_id`,`task_day`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;


```