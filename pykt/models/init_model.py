import torch
import numpy as np
import os
from torch.nn.parallel import DistributedDataParallel as DDP

from .dkt import DKT
from .dkt_plus import DKTPlus
from .dkvmn import DKVMN
from .deep_irt import DeepIRT
from .sakt import SAKT
from .saint import SAINT
from .kqn import KQN
from .atdkt import ATDKT
from .atkt import ATKT
from .dkt_forget import DKTForget
from .akt import AKT
from .akt_conv import AKTConv
from .gkt import GKT
from .gkt_utils import get_gkt_graph
from .lpkt import LPKT
from .lpkt_utils import generate_qmatrix
from .skvmn import SKVMN
from .hawkes import HawkesKT
from .iekt import IEKT
from .bakt_time import BAKTTime
from .qdkt import QDKT
# from .qikt import QIKT
from .dimkt import DIMKT
from .sparsekt import sparseKT
from .bakt_qikt import BAKT_QIKT
from .simplekt_sr import simpleKT_SR
from .stosakt import StosaKT
from .parKT import parKT
from .mikt import MIKT
from .gpt4kt import GPT4KT
from .gnn4kt import GNN4KT
from .simplekt import simpleKT
from .gnn4kt_util import build_graph, load_graph

device = "cpu" if not torch.cuda.is_available() else "cuda"

def init_model(model_name, model_config, data_config, emb_type, args=None, num_stu=None, mode="train", train_start=True):
    if model_name == "dkt":
        model = DKT(data_config["num_c"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "dkt+":
        model = DKTPlus(data_config["num_c"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "dkvmn":
        model = DKVMN(data_config["num_c"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "deep_irt":
        model = DeepIRT(data_config["num_c"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "sakt":
        model = SAKT(data_config["num_c"],  **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "saint":
        model = SAINT(data_config["num_q"], data_config["num_c"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "dkt_forget":
        model = DKTForget(data_config["num_c"], data_config["num_rgap"], data_config["num_sgap"], data_config["num_pcount"], **model_config).to(device)
    elif model_name == "akt":
        model = AKT(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "akt_conv":
        model = AKTConv(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "kqn":
        model = KQN(data_config["num_c"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "atkt":
        model = ATKT(data_config["num_c"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"], fix=False).to(device)
    elif model_name == "atktfix":
        model = ATKT(data_config["num_c"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"], fix=True).to(device)
    elif model_name == "gkt":
        graph_type = model_config['graph_type']
        fname = f"gkt_graph_{graph_type}.npz"
        graph_path = os.path.join(data_config["dpath"], fname)
        if os.path.exists(graph_path):
            graph = torch.tensor(np.load(graph_path, allow_pickle=True)['matrix']).float()
        else:
            graph = get_gkt_graph(data_config["num_c"], data_config["dpath"], 
                    data_config["train_valid_original_file"], data_config["test_original_file"], graph_type=graph_type, tofile=fname)
            graph = torch.tensor(graph).float()
        model = GKT(data_config["num_c"], **model_config,graph=graph,emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "gnn4kt":
        topk = model_config["topk"]
        fname = f"gnn4kt_graph_{topk}.txt"
        graph_path = os.path.join(data_config["dpath"], fname)
        if not os.path.exists(graph_path):
            build_graph(data_config, topk)
        print(f"graph_path:{graph_path}")
        num_q = data_config["num_q"]
        adj = load_graph(graph_path, num_q)
        adj = adj.to(device)
        model = GNN4KT(data_config["num_c"], data_config["num_q"], **model_config, graph=adj,emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "lpkt":
        qmatrix_path = os.path.join(data_config["dpath"], "qmatrix.npz")
        if os.path.exists(qmatrix_path):
            q_matrix = np.load(qmatrix_path, allow_pickle=True)['matrix']
        else:
            q_matrix = generate_qmatrix(data_config)
        q_matrix = torch.tensor(q_matrix).float().to(device)
        model = LPKT(data_config["num_at"], data_config["num_it"], data_config["num_q"], data_config["num_c"], **model_config, q_matrix=q_matrix, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "skvmn":
        model = SKVMN(data_config["num_c"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)   
    elif model_name == "hawkes":
        if data_config["num_q"] == 0 or data_config["num_c"] == 0:
            print(f"model: {model_name} needs questions ans concepts! but the dataset has no both")
            return None
        model = HawkesKT(data_config["num_c"], data_config["num_q"], **model_config)
        model = model.double()
        # print("===before init weights"+"@"*100)
        # model.printparams()
        model.apply(model.init_weights)
        # print("===after init weights")
        # model.printparams()
        model = model.to(device)
    elif model_name == "iekt":
        model = IEKT(num_q=data_config['num_q'], num_c=data_config['num_c'],
                max_concepts=data_config['max_concepts'], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"],device=device).to(device)   
    elif model_name == "qdkt":
        model = QDKT(num_q=data_config['num_q'], num_c=data_config['num_c'],
                max_concepts=data_config['max_concepts'], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"],device=device).to(device)
    # elif model_name == "qikt":
    #     model = QIKT(num_q=data_config['num_q'], num_c=data_config['num_c'],
    #             max_concepts=data_config['max_concepts'], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"],device=device).to(device)
    elif model_name in ["cdkt","atdkt"]:
        model = ATDKT(data_config["num_q"], data_config["num_c"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "bakt_time":
        model = BAKTTime(data_config["num_c"], data_config["num_q"], data_config["num_rgap"], data_config["num_sgap"], data_config["num_pcount"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "bakt":
        model = simpleKT(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "simplekt":
        model = simpleKT(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "gpt4kt":
        # 2） 配置每个进程的gpu
        # if mode == "train" and train_start:
        #     print(f"init torch.distributed.init_process_group")
        #     # torch.distributed.init_process_group(backend='nccl')
        #     # torch.cuda.set_device(args.local_rank)
        if emb_type.find("pt") == -1:
            model = GPT4KT(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
        else:
            model = GPT4KT(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"], num_sgap=data_config["num_sgap"]).to(device)
        if mode == "train" and train_start:
            model = DDP(model)
    elif model_name == "bakt_qikt":
        model = BAKT_QIKT(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "simplekt_sr":
        model = simpleKT_SR(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "parkt":
        if emb_type.find("time") == -1:
            model = parKT(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
        else:
            model = parKT(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"], num_rgap=data_config["num_rgap"], num_sgap=data_config["num_sgap"], num_pcount=data_config["num_pcount"]).to(device)
            # model = parKT(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"], num_rgap=data_config["num_rgap"], num_sgap=data_config["num_sgap"], num_pcount=data_config["num_pcount"], num_it=data_config["num_it"]).to(device)
    elif model_name == "mikt":
        if emb_type.find("time") == -1:
            model = MIKT(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
        else:
            model = MIKT(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"], num_rgap=data_config["num_rgap"], num_sgap=data_config["num_sgap"], num_pcount=data_config["num_pcount"]).to(device)
    elif model_name == "stosakt":
        model = StosaKT(data_config["num_c"], args, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "dimkt":
        model = DIMKT(data_config["num_q"],data_config["num_c"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)
    elif model_name == "sparsekt":
        model = sparseKT(data_config["num_c"], data_config["num_q"], **model_config, emb_type=emb_type, emb_path=data_config["emb_path"]).to(device)          
    else:
        print("The wrong model name was used...")
        return None
    return model
def load_model(model_name, model_config, data_config, emb_type, ckpt_path, args=None):
    model = init_model(model_name, model_config, data_config, emb_type, args, mode="test")
    net = torch.load(os.path.join(ckpt_path, emb_type+"_model.ckpt"))
    model.load_state_dict(net,strict=False)
    return model
