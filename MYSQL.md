## ��Ŀ��mysql���ֶ��Լ���Ϣ
```
    CREATE TABLE `cookies` (
      `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
      `cookies` varchar(1024) DEFAULT NULL,
      `type` varchar(32) DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

	CREATE TABLE `zhihu_question` (
	  `id` varchar(64) NOT NULL COMMENT '֪��question_id',
	  `title` varchar(64) DEFAULT NULL COMMENT '֪���������',
	  `href` varchar(128) DEFAULT NULL COMMENT '֪������url',
	  `create_time` datetime DEFAULT NULL,
	  `update_time` datetime DEFAULT NULL,
	  `execute_type` int(1) DEFAULT '1' COMMENT '1�������ʼ״̬ 2��question_info ������',
	  `is_delete` int(1) DEFAULT '1' COMMENT '�Ƿ񱻹ر�',
	  PRIMARY KEY (`id`),
	  UNIQUE KEY `href�����ظ�` (`href`) USING HASH
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;

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

    CREATE TABLE `zhihu_special` (
      `special_id` int(11) NOT NULL COMMENT 'ר��id',
      `title` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '����',
      `create_time` datetime NOT NULL COMMENT '����ʱ��',
      `update_time` datetime NOT NULL COMMENT '�޸�ʱ��',
      `is_delete` tinyint(1) NOT NULL DEFAULT '1' COMMENT '0��ɾ�� 1��δɾ��',
      PRIMARY KEY (`special_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

	CREATE TABLE `zhihu_topic` (
      `topic_id` int(11) NOT NULL,
      `topic_name` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '������',
      `follow_num` int(11) DEFAULT NULL COMMENT '��ע��',
      `question_num` int(11) DEFAULT NULL COMMENT '������',
      `create_time` datetime NOT NULL,
      `update_time` datetime NOT NULL,
      `is_delete` tinyint(11) unsigned NOT NULL DEFAULT '1' COMMENT '0��ɾ�� 1��δɾ��',
      PRIMARY KEY (`topic_id`),
      KEY `zhihu_topic_name` (`topic_name`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='֪������';

    CREATE TABLE `zhihu_topic_question_relation` (
      `topic_id` int(10) unsigned NOT NULL,
      `question_id` int(10) unsigned NOT NULL,
      `create_time` datetime NOT NULL COMMENT '����ʱ��',
      `update_time` datetime NOT NULL COMMENT '�޸�ʱ��',
      `is_delete` tinyint(1) unsigned NOT NULL DEFAULT '1' COMMENT '0��ɾ�� 1��δɾ��',
      PRIMARY KEY (`topic_id`,`question_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

    CREATE TABLE `zhihu_topic_special_relation` (
      `topic_id` int(11) NOT NULL COMMENT '����id',
      `special_id` int(11) NOT NULL COMMENT 'ר��id',
      `create_time` datetime NOT NULL COMMENT '����ʱ��',
      `update_time` datetime NOT NULL COMMENT '�޸�ʱ��',
      `is_delete` tinyint(4) NOT NULL DEFAULT '1' COMMENT '0��ɾ�� 1��δɾ��',
      PRIMARY KEY (`topic_id`,`special_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;



```
