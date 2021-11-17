-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : ven. 05 nov. 2021 à 11:22
-- Version du serveur : 10.5.9-MariaDB
-- Version de PHP : 7.3.29-to-be-removed-in-future-macOS

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `visioWork`
--

-- --------------------------------------------------------

--
-- Structure de la table `visioServer_dataadmin`
--

CREATE TABLE `visioServer_dataadmin` (
  `id` bigint(20) NOT NULL,
  `dateRef` datetime(6) DEFAULT NULL,
  `currentBase` tinyint(1) NOT NULL,
  `fileNameRef` varchar(128) DEFAULT NULL,
  `version` int(11) NOT NULL,
  `dateVol` datetime(6) DEFAULT NULL,
  `fileNameVol` varchar(128) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Déchargement des données de la table `visioServer_dataadmin`
--

INSERT INTO `visioServer_dataadmin` (`id`, `dateRef`, `currentBase`, `fileNameRef`, `version`, `dateVol`, `fileNameVol`) VALUES
(4, '2021-11-04 17:38:33.786879', 1, 'test.xlsx', 100, NULL, 'New'),
(5, '2021-11-05 11:09:42.075213', 0, 'Referentiel Visio 2021-10-04.xlsx', 101, '2021-11-05 09:39:20.826637', 'Fichier pour Fantasiapp _ volumes par PdV P2CD enduits mortiers Prégy et Salsi à fin 12 2020.xlsx');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `visioServer_dataadmin`
--
ALTER TABLE `visioServer_dataadmin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `version` (`version`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `visioServer_dataadmin`
--
ALTER TABLE `visioServer_dataadmin`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
