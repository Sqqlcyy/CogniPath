# /app/services/tree_builder_service.py

# ----------------- 导入所有必要的模块 -----------------
import os
import pickle
import re
import asyncio
from typing import List, Dict, Set, Tuple

# 使用绝对路径导入RAPTOR库 (假设raptor源代码在 app/raptor/ 目录下)
from app.raptor import RetrievalAugmentation, RetrievalAugmentationConfig
from app.raptor.tree_structures import Tree as RaptorTree, Node as RaptorNode
from app.raptor.FaissRetriever import FaissRetriever, FaissRetrieverConfig
from app.raptor.tree_builder import TreeBuilder # 需要从tree_builder导入create_node

# 导入我们自己的模块
from ..models.custom_raptor_models import (
    SparkQAModel, 
    SparkSummarizationModel, 
    SparkEmbeddingModel
)
from ..models.schemas import DocumentTreeNode

# ----------------- 全局配置 -----------------
TREE_CACHE_DIR = "./tree_cache"
os.makedirs(TREE_CACHE_DIR, exist_ok=True)

# ----------------- 主服务类 -----------------

class TreeBuilderService:
    """
    【最终完整版】
    - 封装所有与RAPTOR交互的逻辑，包括：
    - 定制化模型配置
    - 树的构建与持久化缓存
    - 双检索器(TreeRetriever/FaissRetriever)的初始化与调用
    - 数据格式适配 (RAPTOR Tree -> 前端JSON)
    - 对带时间戳文本的完整处理
    """
    def __init__(self, doc_id: str, use_sbert_for_dev: bool = False):
        if not doc_id:
            raise ValueError("doc_id不能为空")
            
        self.doc_id = doc_id
        self.use_sbert_for_dev = use_sbert_for_dev
        self.tree_path = os.path.join(TREE_CACHE_DIR, f"{self.doc_id}.pkl")
        
        self.raptor_config = self._create_raptor_config()
        self.raptor_instance = self._init_raptor_instance()
        self.faiss_retriever = self._init_faiss_retriever() if self.raptor_instance.tree else None

    # --- --------------------------------- ---
    # ---       初始化与配置方法           ---
    # --- --------------------------------- ---

    def _create_raptor_config(self) -> RetrievalAugmentationConfig:
        """
        【最终版】
        创建我们定制化的RAPTOR配置对象，注入所有自定义的星火模型。
        """
        # 可以通过环境变量或构造函数参数来决定是否使用开发模式
        if self.use_sbert_for_dev:
            print(f"[{self.doc_id}] [DEV MODE] 使用SBERT嵌入模型。")
            embedding_model_instance = SBertEmbeddingModel()
        else:
            print(f"[{self.doc_id}] 使用讯飞星火Embedding API。")
            embedding_model_instance = SparkEmbeddingModel()

        # 【核心装配】: 实例化我们所有定制化的模型
        qa_model_instance = SparkQAModel(model_name="generalv3.5")
        summarization_model_instance = SparkSummarizationModel(model_name="x1")
        
        print(f"[{self.doc_id}] RAPTOR配置完成: QA->SparkV3.5, Summary->SparkX1, Embedding->{type(embedding_model_instance).__name__}")

        # 将这些实例注入到RAPTOR的配置中
        return RetrievalAugmentationConfig(
            qa_model=qa_model_instance,
            summarization_model=summarization_model_instance,
            embedding_model=embedding_model_instance
        )

    def _init_raptor_instance(self) -> RetrievalAugmentation:
        """初始化RAPTOR主实例。如果存在缓存则加载，否则创建新的。"""
        if os.path.exists(self.tree_path):
            print(f"[{self.doc_id}] 发现缓存的树，正在加载...")
            try:
                return RetrievalAugmentation(config=self.raptor_config, tree=self.tree_path)
            except Exception as e:
                print(f"[{self.doc_id}] 加载缓存树失败: {e}。将创建新树。")
        
        return RetrievalAugmentation(config=self.raptor_config)

    def _init_faiss_retriever(self) -> FaissRetriever:
        """基于已构建的树的叶子节点，初始化FaissRetriever。"""
        if not self.raptor_instance.tree:
            return None
            
        print(f"[{self.doc_id}] 正在初始化FaissRetriever以支持全面检索...")
        
        embedding_model = SBERTEmbeddingModel() if self.use_sbert_for_dev else SparkEmbeddingModel(domain="para")
        question_embedding_model = SBERTEmbeddingModel() if self.use_sbert_for_dev else SparkEmbeddingModel(domain="query")

        faiss_config = FaissRetrieverConfig(
            embedding_model=embedding_model,
            question_embedding_model=question_embedding_model,
            top_k=10
        )
        retriever = FaissRetriever(config=faiss_config)
        
        leaf_nodes = [self.raptor_instance.tree.all_nodes[i] for i in self.raptor_instance.tree.leaf_nodes]
        retriever.build_from_leaf_nodes(leaf_nodes)
        
        print(f"[{self.doc_id}] FaissRetriever初始化完成，共索引 {len(leaf_nodes)} 个叶子节点。")
        return retriever

    # --- --------------------------------- ---
    # ---      【全新的核心建树流水线】     ---
    # --- --------------------------------- ---

    def build_tree_from_text(self, raw_text: str, is_timestamped: bool = False) -> List[DocumentTreeNode]:
        """
        【全新核心方法】从文本构建树，并返回前端所需的结构。
        根据 is_timestamped 参数决定是否进行时间戳处理。
        """
        if os.path.exists(self.tree_path):
            print(f"[{self.doc_id}] 发现缓存树，直接加载并返回。")
            self._ensure_raptor_instance_is_ready()
            return self._format_raptor_tree_to_schema()

        print(f"[{self.doc_id}] 开始新的树构建流程...")

        chunks_with_metadata = []
        if is_timestamped:
            clean_text, chunks_with_metadata = self._preprocess_timestamped_text(raw_text)
        else:
            # 对于普通文本，也将其转换为带元数据的块结构
            chunks_with_metadata = [{"text": chunk, "timestamp": None} for chunk in split_text(raw_text, self.raptor_config.tree_builder_config.tokenizer)]
            
        raptor_tree = self._construct_tree_from_chunks(chunks_with_metadata)
        
        with open(self.tree_path, "wb") as f:
            pickle.dump(raptor_tree, f)
        print(f"[{self.doc_id}] 新树已构建并保存到: {self.tree_path}")

        # 将新构建的树加载到实例中
        self.raptor_instance = RetrievalAugmentation(config=self.raptor_config, tree=raptor_tree)
        self.faiss_retriever = self._init_faiss_retriever()

        return self._format_raptor_tree_to_schema()

    def _preprocess_timestamped_text(self, text: str) -> Tuple[str, List[Dict]]:
        """从 "[HH:MM:SS] text" 格式的文本中，分离出纯文本和带时间戳的块。"""
        # ... (此函数与上一版完全一致) ...
        pass
        
    def _construct_tree_from_chunks(self, initial_chunks_with_metadata: List[Dict]) -> RaptorTree:
        """独立的树构建器，模仿了`TreeBuilder`的逻辑，但更透明、可控。"""
        builder_config = self.raptor_config.tree_builder_config
        # 获取RAPTOR配置的TreeBuilder实例，我们需要用它的create_node方法
        tree_builder: TreeBuilder = self.raptor_instance.tree_builder 

        # 步骤1: 创建叶子节点 (Level 0)
        leaf_nodes: Dict[int, RaptorNode] = {}
        node_id_to_timestamp: Dict[int, int] = {}
        
        for i, chunk_data in enumerate(initial_chunks_with_metadata):
            _, node = tree_builder.create_node(i, chunk_data['text'])
            leaf_nodes[i] = node
            if chunk_data.get('timestamp') is not None:
                node_id_to_timestamp[i] = chunk_data['timestamp']
        
        # 步骤2: 逐层向上构建
        all_nodes = leaf_nodes.copy()
        layer_to_nodes = {0: list(leaf_nodes.values())}
        root_nodes_map = tree_builder.construct_tree(leaf_nodes, all_nodes, layer_to_nodes)

        # 步骤3: 组装成一个完整的RaptorTree对象
        final_tree = RaptorTree(
            all_nodes=all_nodes,
            root_nodes=set(root_nodes_map.keys()),
            leaf_nodes=set(leaf_nodes.keys()),
            num_layers=builder_config.num_layers,
            layer_to_nodes=layer_to_nodes
        )
        
        # 将时间戳映射附加到树对象上
        setattr(final_tree, 'node_id_to_timestamp', node_id_to_timestamp)
        
        return final_tree
        
    def _format_raptor_tree_to_schema(self) -> List[DocumentTreeNode]:
        """【适配器核心】将RAPTOR的Tree对象，递归地转换为我们前端需要的JSON树结构。"""
        if not self.raptor_instance or not self.raptor_instance.tree:
            return []

        raptor_tree: RaptorTree = self.raptor_instance.tree
        all_nodes: Dict[int, RaptorNode] = raptor_tree.all_nodes
        timestamp_map = getattr(raptor_tree, 'node_id_to_timestamp', {})
        memo = {}

        def build_frontend_node(node_id: int) -> DocumentTreeNode:
            if node_id in memo:
                return memo[node_id]

            raptor_node = all_nodes.get(node_id)
            if not raptor_node: return None

            children_nodes = [build_frontend_node(child_id) for child_id in sorted(list(raptor_node.children))]
            children_nodes = [node for node in children_nodes if node] # 过滤掉None

            node_type = "section" if children_nodes else "leaf"
            
            frontend_node = DocumentTreeNode(
                id=str(node_id),
                label=raptor_node.text[:120].replace("\n", " "),
                type=node_type,
                children=children_nodes,
                full_text=raptor_node.text,
                timestamp=timestamp_map.get(node_id)
            )
            memo[node_id] = frontend_node
            return frontend_node

        root_node_ids: Set[int] = raptor_tree.root_nodes
        frontend_tree = [build_frontend_node(root_id) for root_id in sorted(list(root_node_ids))]
        
        return [node for node in frontend_tree if node]


    # --- --------------------------------- ---
    # ---      对外暴露的业务逻辑方法      ---
    # --- --------------------------------- ---

    def answer_precise_question(self, question: str) -> Dict:
        """【业务方法1: 精确问答】"""
        self._ensure_raptor_instance_is_ready()
        print(f"[{self.doc_id}] 使用TreeRetriever进行多尺度检索...")
        
        answer, layer_information = self.raptor_instance.answer_question(
            question,
            collapse_tree=False,
            start_layer=self.raptor_instance.tree.num_layers,
            num_layers=self.raptor_instance.tree.num_layers + 1,
            top_k=3,
            return_layer_information=True
        )
        
        source_ids = []
        if layer_information:
            leaf_ids_in_tree = self.raptor_instance.tree.leaf_nodes
            for info in layer_information:
                if info['node_index'] in leaf_ids_in_tree:
                    source_ids.append(str(info['node_index']))
        
        return {"answer": answer, "source_ids": sorted(list(set(source_ids)))}

    def generate_learning_materials(self, topic: str, material_type: str = "exam") -> Dict:
        """【业务方法2: 出题/泛复习】"""
        self._ensure_raptor_instance_is_ready()
        if not self.faiss_retriever:
            # 如果Faiss还没初始化，在这里初始化它
            self.faiss_retriever = self._init_faiss_retriever()
            if not self.faiss_retriever:
                 raise Exception("Faiss检索器初始化失败，无法生成材料。")

        print(f"[{self.doc_id}] 使用FaissRetriever为主题'{topic}'检索全面资料...")
        context = self.faiss_retriever.retrieve(query=topic)
        
        if material_type == "exam":
            prompt = (f"你是一位专业的出题老师。请根据以下【学习资料】，围绕主题“{topic}”，生成一份包含3道选择题和2道简答题的模拟试卷。题目需要全面覆盖资料中的知识点，并提供标准答案。\n\n【学习资料】:\n---\n{context}\n---")
        else:
            prompt = (f"你是一位学习助理。请根据以下【学习资料】，围绕主题“{topic}”，生成一份要点明确、条理清晰的复习大纲。\n\n【学习资料】:\n---\n{context}\n---")
        
        generated_content = self.raptor_instance.qa_model.answer_question(context="", question=prompt)
        
        return {"material_type": material_type, "content": generated_content}

    def _ensure_raptor_instance_is_ready(self):
        """确保raptor_instance及其内部的树已经加载，以便进行问答。"""
        if self.raptor_instance is None or self.raptor_instance.tree is None:
            self.raptor_instance = self._init_raptor_instance()
            if not self.raptor_instance.tree:
                raise Exception(f"文档 {self.doc_id} 的树不存在或无法加载。请先处理文档。")
