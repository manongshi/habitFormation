CATALOG_URL = "https://www.mohrss.gov.cn/xxgk2020/fdzdgknr/zcfg/gfxwj/rcrs/202112/t20211202_429301.html"
CPTA_URL = "https://www.cpta.com.cn/"

CATEGORY_DATA = [
    ("information", "计算机与信息技术", "软件、网络、数据、通信与数字化能力认证", 10),
    ("finance", "财会与金融", "会计、审计、经济、证券与金融专业资格", 20),
    ("law", "法律与知识产权", "法律职业准入及知识产权专业资格", 30),
    ("construction", "建筑与工程", "建造、造价、监理、规划及勘察设计资格", 40),
    ("safety", "消防与安全", "消防、安全生产、应急救援及安全服务资格", 50),
    ("education", "教育与语言", "教师、普通话及语言专业能力考试", 60),
    ("healthcare", "医药与健康", "医师、护理、药学及卫生专业资格", 70),
    ("social", "社会服务与人力", "社会工作、人力资源及公共服务资格", 80),
    ("transportation", "交通与测绘", "交通运输、检测维修及测绘专业资格", 90),
    ("culture", "文化与传媒", "出版、导游、新闻和广播电视资格", 100),
]


def certificate(
    code,
    name,
    category,
    issuer,
    subjects,
    *,
    short_name=None,
    level=None,
    exam_type="水平评价类",
    cycle="通常每年组织，具体以官方公告为准",
    difficulty=3,
    days=90,
    minutes=90,
    tags=None,
    official_url=CPTA_URL,
    featured=False,
    eligibility="报考条件、免试条件及属地要求以当年度官方考试公告为准。",
):
    return {
        "code": code,
        "name": name,
        "short_name": short_name,
        "category_code": category,
        "level": level,
        "issuer": issuer,
        "exam_type": exam_type,
        "exam_cycle": cycle,
        "difficulty": difficulty,
        "recommended_days": days,
        "recommended_daily_minutes": minutes,
        "description": f"面向{category_label(category)}相关学习与从业需求的全国性考试或职业资格项目。",
        "eligibility_summary": eligibility,
        "subjects": subjects,
        "tags": tags or [],
        "official_url": official_url,
        "is_featured": featured,
    }


def category_label(code):
    return dict((item[0], item[1]) for item in CATEGORY_DATA).get(code, "专业")


CERTIFICATE_DATA = [
    # 计算机与信息技术
    certificate("ruankao-junior", "计算机技术与软件专业技术资格（初级）", "information", "工业和信息化部、人力资源社会保障部", ["计算机基础", "信息技术基础", "专业实务"], short_name="软考初级", level="初级", difficulty=2, days=60, featured=True, official_url="https://www.ruankao.org.cn/", tags=["职称", "IT"]),
    certificate("ruankao-middle", "计算机技术与软件专业技术资格（中级）", "information", "工业和信息化部、人力资源社会保障部", ["基础知识", "应用技术", "案例分析"], short_name="软考中级", level="中级", difficulty=4, days=120, minutes=120, featured=True, official_url="https://www.ruankao.org.cn/", tags=["职称", "项目管理", "软件"]),
    certificate("ruankao-senior", "计算机技术与软件专业技术资格（高级）", "information", "工业和信息化部、人力资源社会保障部", ["综合知识", "案例分析", "论文写作"], short_name="软考高级", level="高级", difficulty=5, days=180, minutes=150, featured=True, official_url="https://www.ruankao.org.cn/", tags=["高级职称", "架构", "项目管理"]),
    certificate("ncre-1", "全国计算机等级考试一级", "information", "教育部教育考试院", ["计算机基础", "办公软件应用", "信息素养"], short_name="NCRE 一级", level="一级", difficulty=1, days=30, minutes=60, official_url="https://ncre.neea.edu.cn/", tags=["办公", "基础"]),
    certificate("ncre-2", "全国计算机等级考试二级", "information", "教育部教育考试院", ["公共基础知识", "程序设计或办公高级应用", "上机操作"], short_name="NCRE 二级", level="二级", difficulty=2, days=60, featured=True, official_url="https://ncre.neea.edu.cn/", tags=["Python", "Java", "Office"]),
    certificate("ncre-3", "全国计算机等级考试三级", "information", "教育部教育考试院", ["网络技术", "数据库技术", "信息安全", "嵌入式或Linux"], short_name="NCRE 三级", level="三级", difficulty=3, days=90, official_url="https://ncre.neea.edu.cn/", tags=["网络", "数据库", "安全"]),
    certificate("ncre-4", "全国计算机等级考试四级", "information", "教育部教育考试院", ["操作系统原理", "计算机组成", "计算机网络", "数据库原理"], short_name="NCRE 四级", level="四级", difficulty=4, days=120, official_url="https://ncre.neea.edu.cn/", tags=["计算机原理"]),
    certificate("communication-junior", "通信专业技术人员职业水平考试（初级）", "information", "工业和信息化部、人力资源社会保障部", ["通信专业综合能力", "通信专业实务"], level="初级", difficulty=2, days=60, tags=["通信"]),
    certificate("communication-middle", "通信专业技术人员职业水平考试（中级）", "information", "工业和信息化部、人力资源社会保障部", ["通信专业综合能力", "通信专业实务"], level="中级", difficulty=4, days=120, tags=["通信", "工程"]),

    # 财会与金融
    certificate("accounting-junior", "初级会计专业技术资格", "finance", "财政部、人力资源社会保障部", ["初级会计实务", "经济法基础"], short_name="初级会计", level="初级", difficulty=2, days=90, featured=True, official_url="https://kzp.mof.gov.cn/", tags=["会计", "职称"]),
    certificate("accounting-middle", "中级会计专业技术资格", "finance", "财政部、人力资源社会保障部", ["中级会计实务", "财务管理", "经济法"], short_name="中级会计", level="中级", difficulty=4, days=180, minutes=120, official_url="https://kzp.mof.gov.cn/", tags=["会计", "职称"]),
    certificate("accounting-senior", "高级会计专业技术资格", "finance", "财政部、人力资源社会保障部", ["高级会计实务"], short_name="高级会计", level="高级", difficulty=5, days=180, minutes=120, official_url="https://kzp.mof.gov.cn/", tags=["高级职称"]),
    certificate("cpa", "注册会计师全国统一考试", "finance", "财政部注册会计师考试委员会", ["会计", "审计", "财务成本管理", "经济法", "税法", "公司战略与风险管理"], short_name="CPA", difficulty=5, days=240, minutes=150, featured=True, official_url="https://www.cicpa.org.cn/", tags=["审计", "财会"]),
    certificate("tax-agent", "税务师职业资格", "finance", "中国注册税务师协会", ["税法一", "税法二", "涉税服务实务", "涉税服务相关法律", "财务与会计"], short_name="税务师", difficulty=4, days=180, minutes=120, official_url="https://www.cctaa.cn/", tags=["税务"]),
    certificate("economist-junior", "初级经济专业技术资格", "finance", "人力资源社会保障部", ["经济基础知识", "专业知识和实务"], short_name="初级经济师", level="初级", difficulty=2, days=75, tags=["职称", "经济"]),
    certificate("economist-middle", "中级经济专业技术资格", "finance", "人力资源社会保障部", ["经济基础知识", "专业知识和实务"], short_name="中级经济师", level="中级", difficulty=3, days=120, featured=True, tags=["职称", "经济"]),
    certificate("economist-senior", "高级经济专业技术资格", "finance", "人力资源社会保障部", ["高级经济实务"], short_name="高级经济师", level="高级", difficulty=4, days=150, tags=["高级职称"]),
    certificate("auditor", "审计专业技术资格", "finance", "审计署、人力资源社会保障部", ["审计相关基础知识", "审计理论与实务"], short_name="审计师", difficulty=3, days=120, tags=["审计", "职称"]),
    certificate("banking", "银行业专业人员职业资格", "finance", "中国银行业协会", ["银行业法律法规与综合能力", "银行业专业实务"], short_name="银行从业", difficulty=2, days=60, official_url="https://www.china-cba.net/", tags=["银行"]),
    certificate("securities", "证券行业专业人员水平评价测试", "finance", "中国证券业协会", ["金融市场基础知识", "证券市场基本法律法规"], short_name="证券从业", difficulty=2, days=60, official_url="https://www.sac.net.cn/", tags=["证券"]),
    certificate("fund", "基金从业人员资格考试", "finance", "中国证券投资基金业协会", ["基金法律法规", "证券投资基金基础知识", "私募股权投资基金基础知识"], short_name="基金从业", difficulty=2, days=60, official_url="https://www.amac.org.cn/", tags=["基金"]),
    certificate("futures", "期货从业人员资格考试", "finance", "中国期货业协会", ["期货基础知识", "期货法律法规"], short_name="期货从业", difficulty=3, days=75, official_url="https://www.cfachina.org/", tags=["期货"]),
    certificate("asset-appraiser", "资产评估师职业资格", "finance", "中国资产评估协会", ["资产评估基础", "资产评估相关知识", "资产评估实务一", "资产评估实务二"], short_name="资产评估师", difficulty=4, days=150, official_url="https://www.cas.org.cn/", tags=["评估"]),

    # 法律与知识产权
    certificate("legal-qualification", "国家统一法律职业资格考试", "law", "中华人民共和国司法部", ["客观题卷一", "客观题卷二", "主观题"], short_name="法考", exam_type="准入类", difficulty=5, days=240, minutes=180, featured=True, official_url="https://www.moj.gov.cn/", tags=["法律", "准入"]),
    certificate("patent-agent", "专利代理师资格考试", "law", "国家知识产权局", ["专利法律知识", "相关法律知识", "专利代理实务"], short_name="专利代理师", exam_type="准入类", difficulty=4, days=150, official_url="https://www.cnipa.gov.cn/", tags=["知识产权"]),

    # 建筑与工程
    certificate("constructor-1", "一级建造师职业资格", "construction", "住房城乡建设部、人力资源社会保障部", ["建设工程经济", "建设工程法规", "建设工程项目管理", "专业工程管理与实务"], short_name="一建", exam_type="准入类", difficulty=5, days=180, minutes=150, featured=True, tags=["建造", "项目管理"]),
    certificate("constructor-2", "二级建造师执业资格", "construction", "省级人力资源社会保障、住房城乡建设主管部门", ["建设工程法规", "建设工程施工管理", "专业工程管理与实务"], short_name="二建", exam_type="准入类", difficulty=3, days=120, featured=True, tags=["建造"]),
    certificate("cost-engineer-1", "一级造价工程师职业资格", "construction", "住房城乡建设部、交通运输部、水利部、人力资源社会保障部", ["建设工程造价管理", "建设工程计价", "建设工程技术与计量", "建设工程造价案例分析"], short_name="一造", exam_type="准入类", difficulty=5, days=180, minutes=150, tags=["造价"]),
    certificate("cost-engineer-2", "二级造价工程师职业资格", "construction", "省级相关主管部门", ["建设工程造价管理基础知识", "建设工程计量与计价实务"], short_name="二造", exam_type="准入类", difficulty=3, days=120, tags=["造价"]),
    certificate("supervision-engineer", "监理工程师职业资格", "construction", "住房城乡建设部、交通运输部、水利部、人力资源社会保障部", ["建设工程监理基本理论和相关法规", "建设工程合同管理", "建设工程目标控制", "建设工程监理案例分析"], short_name="监理工程师", exam_type="准入类", difficulty=4, days=150, tags=["监理"]),
    certificate("consulting-engineer", "咨询工程师（投资）职业资格", "construction", "国家发展改革委、人力资源社会保障部", ["宏观经济政策与发展规划", "工程项目组织与管理", "项目决策分析与评价", "现代咨询方法与实务"], short_name="咨询工程师", difficulty=4, days=150, tags=["咨询", "投资"]),
    certificate("architect-1", "一级注册建筑师资格", "construction", "全国注册建筑师管理委员会", ["建筑设计", "建筑经济施工与设计业务管理", "设计前期与场地设计", "建筑结构建筑物理与设备", "建筑方案设计"], short_name="一级建筑师", exam_type="准入类", difficulty=5, days=240, minutes=150, tags=["建筑设计"]),
    certificate("architect-2", "二级注册建筑师资格", "construction", "全国注册建筑师管理委员会", ["建筑设计建筑材料与构造", "建筑经济施工与设计业务管理", "建筑结构抗震与设备", "场地与建筑方案设计"], short_name="二级建筑师", exam_type="准入类", difficulty=4, days=180, tags=["建筑设计"]),
    certificate("urban-planner", "注册城乡规划师职业资格", "construction", "自然资源部、人力资源社会保障部", ["城乡规划原理", "城乡规划相关知识", "城乡规划管理与法规", "城乡规划实务"], short_name="城乡规划师", exam_type="准入类", difficulty=4, days=150, tags=["规划"]),
    certificate("environment-impact", "环境影响评价工程师职业资格", "construction", "生态环境部、人力资源社会保障部", ["环境影响评价相关法律法规", "技术导则与标准", "技术方法", "案例分析"], short_name="环评工程师", exam_type="准入类", difficulty=4, days=150, tags=["环保"]),
    certificate("electrical-engineer", "注册电气工程师资格", "construction", "住房城乡建设部、人力资源社会保障部", ["公共基础", "专业基础", "专业知识", "专业案例"], short_name="注册电气工程师", exam_type="准入类", difficulty=5, days=240, tags=["勘察设计", "电气"]),
    certificate("civil-engineer", "注册土木工程师资格", "construction", "住房城乡建设部、人力资源社会保障部", ["公共基础", "专业基础", "专业知识", "专业案例"], short_name="注册土木工程师", exam_type="准入类", difficulty=5, days=240, tags=["岩土", "道路", "水利"]),
    certificate("structural-engineer", "注册结构工程师资格", "construction", "住房城乡建设部、人力资源社会保障部", ["基础考试", "专业考试"], short_name="注册结构工程师", exam_type="准入类", difficulty=5, days=240, tags=["结构"]),
    certificate("chemical-engineer", "注册化工工程师资格", "construction", "住房城乡建设部、人力资源社会保障部", ["公共基础", "专业基础", "专业知识", "专业案例"], short_name="注册化工工程师", exam_type="准入类", difficulty=5, days=210, tags=["化工"]),

    # 消防与安全
    certificate("fire-engineer-1", "一级注册消防工程师资格", "safety", "应急管理部、人力资源社会保障部", ["消防安全技术实务", "消防安全技术综合能力", "消防安全案例分析"], short_name="一级消防工程师", exam_type="准入类", difficulty=5, days=180, minutes=150, featured=True, tags=["消防", "工程"]),
    certificate("fire-facility-operator", "消防设施操作员", "safety", "消防行业职业技能鉴定机构", ["理论知识", "技能操作"], short_name="消控证", exam_type="准入类", difficulty=2, days=60, featured=True, official_url="https://xfhyjd.119.gov.cn/", tags=["消防", "技能"]),
    certificate("safety-engineer", "中级注册安全工程师职业资格", "safety", "应急管理部、人力资源社会保障部", ["安全生产法律法规", "安全生产管理", "安全生产技术基础", "安全生产专业实务"], short_name="注安师", exam_type="准入类", difficulty=4, days=150, tags=["安全生产"]),
    certificate("emergency-rescuer", "应急救援员职业资格", "safety", "应急救援行业职业技能鉴定机构", ["理论知识", "应急救援技能"], short_name="应急救援员", difficulty=2, days=45, official_url=CATALOG_URL, tags=["应急", "技能"]),

    # 教育与语言
    certificate("teacher-kindergarten", "幼儿园教师资格考试", "education", "教育部教育考试院", ["综合素质", "保教知识与能力", "面试"], short_name="幼儿教资", exam_type="准入类", difficulty=2, days=75, official_url="https://ntce.neea.edu.cn/", tags=["教师", "幼儿"]),
    certificate("teacher-primary", "小学教师资格考试", "education", "教育部教育考试院", ["综合素质", "教育教学知识与能力", "面试"], short_name="小学教资", exam_type="准入类", difficulty=2, days=75, featured=True, official_url="https://ntce.neea.edu.cn/", tags=["教师", "小学"]),
    certificate("teacher-secondary", "中学教师资格考试", "education", "教育部教育考试院", ["综合素质", "教育知识与能力", "学科知识与教学能力", "面试"], short_name="中学教资", exam_type="准入类", difficulty=3, days=90, official_url="https://ntce.neea.edu.cn/", tags=["教师", "中学"]),
    certificate("mandarin", "普通话水平测试", "education", "国家语言文字工作部门", ["读单音节字词", "读多音节词语", "朗读短文", "命题说话"], short_name="普通话证书", difficulty=1, days=30, minutes=45, official_url="https://www.cltt.org/", tags=["语言"]),
    certificate("catti", "翻译专业资格（水平）考试", "education", "中国外文局、人力资源社会保障部", ["翻译综合能力", "翻译实务"], short_name="CATTI", difficulty=4, days=150, official_url="https://www.catticenter.com/", tags=["翻译", "语言"]),

    # 医药与健康
    certificate("physician", "医师资格考试", "healthcare", "国家卫生健康委员会", ["医学综合考试", "实践技能考试"], short_name="执业医师", exam_type="准入类", difficulty=5, days=240, minutes=150, featured=True, official_url="https://www.nmec.org.cn/", tags=["医疗", "准入"]),
    certificate("assistant-physician", "执业助理医师资格考试", "healthcare", "国家卫生健康委员会", ["医学综合考试", "实践技能考试"], short_name="助理医师", exam_type="准入类", difficulty=4, days=180, official_url="https://www.nmec.org.cn/", tags=["医疗"]),
    certificate("nurse", "护士执业资格考试", "healthcare", "国家卫生健康委员会、人力资源社会保障部", ["专业实务", "实践能力"], short_name="护士资格", exam_type="准入类", difficulty=3, days=120, featured=True, official_url="https://www.21wecan.com/", tags=["护理"]),
    certificate("pharmacist-western", "执业药师职业资格（药学）", "healthcare", "国家药品监督管理局、人力资源社会保障部", ["药学专业知识一", "药学专业知识二", "药事管理与法规", "药学综合知识与技能"], short_name="执业西药师", exam_type="准入类", difficulty=4, days=180, tags=["药学"]),
    certificate("pharmacist-chinese", "执业药师职业资格（中药学）", "healthcare", "国家药品监督管理局、人力资源社会保障部", ["中药学专业知识一", "中药学专业知识二", "药事管理与法规", "中药学综合知识与技能"], short_name="执业中药师", exam_type="准入类", difficulty=4, days=180, tags=["中药"]),
    certificate("health-professional", "卫生专业技术资格考试", "healthcare", "国家卫生健康委员会、人力资源社会保障部", ["基础知识", "相关专业知识", "专业知识", "专业实践能力"], short_name="卫生资格", difficulty=4, days=150, official_url="https://www.21wecan.com/", tags=["卫生职称"]),

    # 社会服务与人力
    certificate("social-worker-assistant", "助理社会工作师职业资格", "social", "民政部、人力资源社会保障部", ["社会工作综合能力", "社会工作实务"], short_name="初级社工", level="初级", difficulty=2, days=75, featured=True, tags=["社工"]),
    certificate("social-worker", "社会工作师职业资格", "social", "民政部、人力资源社会保障部", ["社会工作综合能力", "社会工作法规与政策", "社会工作实务"], short_name="中级社工", level="中级", difficulty=3, days=120, tags=["社工"]),
    certificate("social-worker-senior", "高级社会工作师职业资格", "social", "民政部、人力资源社会保障部", ["社会工作实务"], short_name="高级社工", level="高级", difficulty=4, days=150, tags=["社工", "高级"]),
    certificate("hr-economist", "经济专业技术资格（人力资源管理）", "social", "人力资源社会保障部", ["经济基础知识", "人力资源管理专业知识和实务"], short_name="人力资源经济师", difficulty=3, days=120, tags=["人力资源", "职称"]),

    # 交通与测绘
    certificate("surveyor", "注册测绘师资格", "transportation", "自然资源部、人力资源社会保障部", ["测绘综合能力", "测绘管理与法律法规", "测绘案例分析"], short_name="注册测绘师", exam_type="准入类", difficulty=4, days=150, tags=["测绘"]),
    certificate("road-water-testing", "公路水运工程试验检测专业技术人员职业资格", "transportation", "交通运输部职业资格中心", ["公共基础", "道路工程", "桥梁隧道工程", "交通工程", "水运材料或结构地基"], short_name="公路水运检测", difficulty=4, days=150, official_url="https://www.jtzyzg.org.cn/", tags=["交通", "检测"]),
    certificate("vehicle-maintenance", "机动车检测维修专业技术人员职业资格", "transportation", "交通运输部、人力资源社会保障部", ["机动车检测维修法规与技术", "专业实务"], short_name="机动车检测维修", difficulty=3, days=90, official_url="https://www.jtzyzg.org.cn/", tags=["汽车", "维修"]),

    # 文化与传媒
    certificate("publisher", "出版专业技术人员职业资格", "culture", "国家新闻出版署、人力资源社会保障部", ["出版专业基础知识", "出版专业理论与实务"], short_name="出版资格", difficulty=3, days=120, tags=["出版", "职称"]),
    certificate("tour-guide", "全国导游资格考试", "culture", "文化和旅游部", ["政策与法律法规", "导游业务", "全国导游基础知识", "地方导游基础知识", "导游服务能力"], short_name="导游证", exam_type="准入类", difficulty=3, days=90, featured=True, official_url="https://zwfw.mct.gov.cn/", tags=["旅游", "服务"]),
    certificate("journalist", "新闻记者职业资格考试", "culture", "国家新闻出版署、人力资源社会保障部", ["新闻基础知识", "新闻采编实务"], short_name="记者资格", exam_type="准入类", difficulty=3, days=90, tags=["新闻", "传媒"]),
    certificate("broadcast-host", "广播电视播音员主持人资格考试", "culture", "国家广播电视总局", ["综合知识", "广播电视基础知识", "播音主持业务", "口试"], short_name="播音员主持人资格", exam_type="准入类", difficulty=3, days=90, official_url="https://www.nrta.gov.cn/", tags=["播音", "传媒"]),
]
